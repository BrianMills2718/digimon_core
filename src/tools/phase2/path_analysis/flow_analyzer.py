"""Flow Analyzer

Implements flow analysis algorithms for network analysis.
"""

import networkx as nx
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from .path_data_models import FlowAlgorithm, FlowResult
from src.core.logging_config import get_logger

logger = get_logger(__name__)


class FlowAnalyzer:
    """Analyze network flows using various algorithms"""
    
    def analyze_flows(self, graph: nx.Graph, input_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze network flows between source-sink pairs"""
        try:
            sources = input_data.get('flow_sources', [])
            sinks = input_data.get('flow_sinks', [])
            capacity_attr = input_data.get('capacity_attribute', 'capacity')
            
            # Default to using graph structure if no sources/sinks specified
            if not sources and not sinks:
                nodes = list(graph.nodes())
                if len(nodes) >= 2:
                    sources = [nodes[0]]
                    sinks = [nodes[-1]]
                else:
                    logger.warning("Insufficient nodes for flow analysis")
                    return []
            
            # Ensure graph is directed for flow analysis
            if not graph.is_directed():
                logger.info("Converting undirected graph to directed for flow analysis")
                flow_graph = graph.to_directed()
            else:
                flow_graph = graph.copy()
            
            # Add default capacities if not present
            self._ensure_capacities(flow_graph, capacity_attr)
            
            results = []
            
            # Analyze flow for each source-sink pair
            for source in sources:
                for sink in sinks:
                    if source == sink:
                        continue
                    
                    if source not in flow_graph.nodes or sink not in flow_graph.nodes:
                        logger.warning(f"Source {source} or sink {sink} not in graph")
                        continue
                    
                    try:
                        flow_result = self._compute_max_flow(flow_graph, source, sink, capacity_attr)
                        results.append(flow_result)
                    except Exception as e:
                        logger.error(f"Flow analysis failed for {source}->{sink}: {e}")
                        error_result = FlowResult(
                            source=source,
                            sink=sink,
                            max_flow_value=0,
                            min_cut_edges=[],
                            flow_dict={},
                            algorithm="max_flow",
                            metadata={"error": str(e), "computed_at": datetime.now().isoformat()}
                        )
                        results.append(error_result.to_dict())
            
            return results
            
        except Exception as e:
            logger.error(f"Error in flow analysis: {e}")
            return [{"error": str(e)}]
    
    def _ensure_capacities(self, graph: nx.Graph, capacity_attr: str):
        """Ensure all edges have capacity attributes"""
        for u, v, data in graph.edges(data=True):
            if capacity_attr not in data:
                # Use weight as capacity if available, otherwise default to 1
                if 'weight' in data:
                    data[capacity_attr] = data['weight']
                else:
                    data[capacity_attr] = 1.0
    
    def _compute_max_flow(self, graph: nx.Graph, source: str, sink: str, 
                         capacity_attr: str) -> Dict[str, Any]:
        """Compute maximum flow using Ford-Fulkerson algorithm"""
        try:
            # Compute maximum flow
            flow_value, flow_dict = nx.maximum_flow(graph, source, sink, capacity=capacity_attr)
            
            # Compute minimum cut
            cut_value, (reachable, non_reachable) = nx.minimum_cut(graph, source, sink, capacity=capacity_attr)
            
            # Find cut edges
            cut_edges = []
            for u in reachable:
                for v in non_reachable:
                    if graph.has_edge(u, v):
                        capacity = graph[u][v].get(capacity_attr, 1.0)
                        cut_edges.append((u, v, capacity))
            
            # Analyze flow paths
            flow_paths = self._extract_flow_paths(flow_dict, source, sink)
            
            # Calculate flow statistics
            flow_stats = self._calculate_flow_statistics(flow_dict, graph, capacity_attr)
            
            flow_result = FlowResult(
                source=source,
                sink=sink,
                max_flow_value=flow_value,
                min_cut_edges=cut_edges,
                flow_dict=flow_dict,
                algorithm="ford_fulkerson",
                metadata={
                    "capacity_attribute": capacity_attr,
                    "cut_value": cut_value,
                    "reachable_nodes": len(reachable),
                    "non_reachable_nodes": len(non_reachable),
                    "flow_paths": flow_paths,
                    "flow_statistics": flow_stats,
                    "computed_at": datetime.now().isoformat()
                }
            )
            
            return flow_result.to_dict()
            
        except Exception as e:
            logger.error(f"Max flow computation failed: {e}")
            raise e
    
    def _extract_flow_paths(self, flow_dict: Dict[str, Dict[str, float]], 
                           source: str, sink: str) -> List[Dict[str, Any]]:
        """Extract individual flow paths from flow dictionary"""
        try:
            paths = []
            
            # Simple path extraction - find paths with positive flow
            def find_paths(current, target, path, visited, flow_remaining):
                if current == target and flow_remaining > 0:
                    paths.append({
                        "path": path + [current],
                        "flow": flow_remaining,
                        "length": len(path)
                    })
                    return
                
                if current in visited:
                    return
                
                visited.add(current)
                
                if current in flow_dict:
                    for next_node, flow in flow_dict[current].items():
                        if flow > 0 and next_node not in visited:
                            min_flow = min(flow_remaining, flow)
                            find_paths(next_node, target, path + [current], visited.copy(), min_flow)
            
            # Start path finding from source
            if source in flow_dict:
                for next_node, flow in flow_dict[source].items():
                    if flow > 0:
                        find_paths(next_node, sink, [source], set(), flow)
            
            return paths[:10]  # Limit to first 10 paths
            
        except Exception as e:
            logger.error(f"Path extraction failed: {e}")
            return []
    
    def _calculate_flow_statistics(self, flow_dict: Dict[str, Dict[str, float]], 
                                  graph: nx.Graph, capacity_attr: str) -> Dict[str, Any]:
        """Calculate flow utilization statistics"""
        try:
            total_flow = 0
            total_capacity = 0
            utilized_edges = 0
            total_edges = 0
            
            for u, v, data in graph.edges(data=True):
                capacity = data.get(capacity_attr, 1.0)
                flow = flow_dict.get(u, {}).get(v, 0)
                
                total_capacity += capacity
                total_flow += flow
                total_edges += 1
                
                if flow > 0:
                    utilized_edges += 1
            
            utilization_ratio = total_flow / total_capacity if total_capacity > 0 else 0
            edge_utilization_ratio = utilized_edges / total_edges if total_edges > 0 else 0
            
            return {
                "total_flow": total_flow,
                "total_capacity": total_capacity,
                "utilization_ratio": utilization_ratio,
                "utilized_edges": utilized_edges,
                "total_edges": total_edges,
                "edge_utilization_ratio": edge_utilization_ratio
            }
            
        except Exception as e:
            logger.error(f"Flow statistics calculation failed: {e}")
            return {}
    
    def analyze_network_flow_properties(self, graph: nx.Graph, 
                                       input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze general network flow properties"""
        try:
            capacity_attr = input_data.get('capacity_attribute', 'capacity')
            
            # Ensure directed graph
            if not graph.is_directed():
                flow_graph = graph.to_directed()
            else:
                flow_graph = graph.copy()
            
            self._ensure_capacities(flow_graph, capacity_attr)
            
            # Calculate network-wide flow properties
            properties = {
                "total_capacity": sum(data.get(capacity_attr, 1.0) 
                                    for u, v, data in flow_graph.edges(data=True)),
                "average_capacity": np.mean([data.get(capacity_attr, 1.0) 
                                           for u, v, data in flow_graph.edges(data=True)]),
                "capacity_distribution": self._analyze_capacity_distribution(flow_graph, capacity_attr),
                "network_connectivity": self._analyze_flow_connectivity(flow_graph),
                "bottleneck_analysis": self._identify_bottlenecks(flow_graph, capacity_attr)
            }
            
            return properties
            
        except Exception as e:
            logger.error(f"Network flow properties analysis failed: {e}")
            return {"error": str(e)}
    
    def _analyze_capacity_distribution(self, graph: nx.Graph, capacity_attr: str) -> Dict[str, Any]:
        """Analyze the distribution of edge capacities"""
        try:
            capacities = [data.get(capacity_attr, 1.0) for u, v, data in graph.edges(data=True)]
            
            if not capacities:
                return {}
            
            return {
                "min_capacity": min(capacities),
                "max_capacity": max(capacities),
                "mean_capacity": np.mean(capacities),
                "median_capacity": np.median(capacities),
                "std_capacity": np.std(capacities),
                "capacity_range": max(capacities) - min(capacities),
                "unique_capacities": len(set(capacities))
            }
            
        except Exception as e:
            logger.error(f"Capacity distribution analysis failed: {e}")
            return {}
    
    def _analyze_flow_connectivity(self, graph: nx.Graph) -> Dict[str, Any]:
        """Analyze connectivity from flow perspective"""
        try:
            # Basic connectivity measures
            connectivity = {
                "strongly_connected": nx.is_strongly_connected(graph),
                "weakly_connected": nx.is_weakly_connected(graph),
                "number_of_components": nx.number_strongly_connected_components(graph)
            }
            
            # Node connectivity (minimum number of nodes to remove to disconnect)
            try:
                connectivity["node_connectivity"] = nx.node_connectivity(graph)
                connectivity["edge_connectivity"] = nx.edge_connectivity(graph)
            except:
                connectivity["node_connectivity"] = None
                connectivity["edge_connectivity"] = None
            
            return connectivity
            
        except Exception as e:
            logger.error(f"Flow connectivity analysis failed: {e}")
            return {}
    
    def _identify_bottlenecks(self, graph: nx.Graph, capacity_attr: str) -> Dict[str, Any]:
        """Identify potential bottlenecks in the network"""
        try:
            # Find edges with lowest capacities
            edge_capacities = [(u, v, data.get(capacity_attr, 1.0)) 
                             for u, v, data in graph.edges(data=True)]
            
            if not edge_capacities:
                return {}
            
            # Sort by capacity
            sorted_edges = sorted(edge_capacities, key=lambda x: x[2])
            
            # Identify bottleneck edges (bottom 10% by capacity)
            bottleneck_count = max(1, len(sorted_edges) // 10)
            bottleneck_edges = sorted_edges[:bottleneck_count]
            
            # Identify nodes that are potential bottlenecks
            bottleneck_nodes = set()
            for u, v, capacity in bottleneck_edges:
                bottleneck_nodes.add(u)
                bottleneck_nodes.add(v)
            
            return {
                "bottleneck_edges": [(u, v, cap) for u, v, cap in bottleneck_edges],
                "bottleneck_nodes": list(bottleneck_nodes),
                "min_capacity": sorted_edges[0][2] if sorted_edges else 0,
                "bottleneck_threshold": sorted_edges[bottleneck_count-1][2] if bottleneck_edges else 0,
                "bottleneck_edge_count": len(bottleneck_edges),
                "bottleneck_node_count": len(bottleneck_nodes)
            }
            
        except Exception as e:
            logger.error(f"Bottleneck identification failed: {e}")
            return {}