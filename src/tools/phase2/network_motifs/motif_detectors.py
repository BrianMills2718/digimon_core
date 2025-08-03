"""Network Motif Detection Algorithms

Implements various motif detection algorithms for graph analysis.
"""

import networkx as nx
import numpy as np
from typing import Dict, List, Tuple, Set, Any
from collections import defaultdict
import itertools

from .motif_data_models import MotifType, MotifInstance, MotifDetectionConfig
from src.core.logging_config import get_logger

logger = get_logger(__name__)


class MotifDetector:
    """Detect various types of network motifs"""
    
    def __init__(self):
        self.motif_configs = MotifDetectionConfig.get_default_configs()
    
    def detect_motifs(self, graph: nx.Graph, motif_types: List[MotifType], 
                     min_frequency: int = 1, max_instances: int = 10000) -> List[MotifInstance]:
        """Detect specified motif types in the graph"""
        try:
            all_motifs = []
            
            for motif_type in motif_types:
                if motif_type == MotifType.ALL:
                    # Detect all motif types
                    for mt in MotifType:
                        if mt != MotifType.ALL:
                            motifs = self._detect_specific_motif(graph, mt, min_frequency, max_instances)
                            all_motifs.extend(motifs)
                else:
                    motifs = self._detect_specific_motif(graph, motif_type, min_frequency, max_instances)
                    all_motifs.extend(motifs)
            
            logger.info(f"Detected {len(all_motifs)} total motif instances")
            return all_motifs
            
        except Exception as e:
            logger.error(f"Motif detection failed: {e}")
            return []
    
    def _detect_specific_motif(self, graph: nx.Graph, motif_type: MotifType, 
                              min_frequency: int, max_instances: int) -> List[MotifInstance]:
        """Detect a specific type of motif"""
        try:
            if motif_type == MotifType.TRIANGLES:
                return self._detect_triangles(graph, min_frequency)
            elif motif_type == MotifType.SQUARES:
                return self._detect_squares(graph, min_frequency)
            elif motif_type == MotifType.WEDGES:
                return self._detect_wedges(graph, min_frequency)
            elif motif_type == MotifType.FEED_FORWARD_LOOPS:
                return self._detect_feed_forward_loops(graph, min_frequency)
            elif motif_type == MotifType.BI_FANS:
                return self._detect_bi_fans(graph, min_frequency)
            elif motif_type == MotifType.THREE_CHAINS:
                return self._detect_chains(graph, 3, min_frequency)
            elif motif_type == MotifType.FOUR_CHAINS:
                return self._detect_chains(graph, 4, min_frequency)
            elif motif_type == MotifType.CLIQUES:
                return self._detect_cliques(graph, [3, 4, 5], min_frequency)
            else:
                logger.warning(f"Unknown motif type: {motif_type}")
                return []
                
        except Exception as e:
            logger.error(f"Detection of {motif_type} failed: {e}")
            return []
    
    def _detect_triangles(self, graph: nx.Graph, min_frequency: int) -> List[MotifInstance]:
        """Detect triangle motifs (3-cliques)"""
        try:
            triangles = []
            triangle_count = 0
            
            # Use NetworkX triangle detection
            for triangle in nx.enumerate_all_cliques(graph):
                if len(triangle) == 3:
                    triangle_count += 1
                    nodes = list(triangle)
                    edges = [(nodes[i], nodes[j]) for i in range(3) for j in range(i+1, 3) 
                            if graph.has_edge(nodes[i], nodes[j])]
                    
                    motif = MotifInstance(
                        motif_type="triangles",
                        nodes=nodes,
                        edges=edges,
                        pattern_id=f"triangle_{triangle_count}",
                        significance_score=1.0,
                        frequency=1
                    )
                    triangles.append(motif)
                    
                    if len(triangles) >= 10000:  # Limit for performance
                        break
            
            logger.info(f"Detected {len(triangles)} triangles")
            return triangles
            
        except Exception as e:
            logger.error(f"Triangle detection failed: {e}")
            return []
    
    def _detect_squares(self, graph: nx.Graph, min_frequency: int) -> List[MotifInstance]:
        """Detect square motifs (4-cycles)"""
        try:
            squares = []
            square_count = 0
            
            # Convert to undirected for cycle detection
            if graph.is_directed():
                undirected = graph.to_undirected()
            else:
                undirected = graph
            
            # Find 4-cycles using simple cycle detection
            try:
                cycles = nx.simple_cycles(undirected.to_directed(), length_bound=4)
                for cycle in cycles:
                    if len(cycle) == 4:
                        square_count += 1
                        nodes = list(cycle)
                        edges = [(nodes[i], nodes[(i+1) % 4]) for i in range(4) 
                                if graph.has_edge(nodes[i], nodes[(i+1) % 4])]
                        
                        motif = MotifInstance(
                            motif_type="squares",
                            nodes=nodes,
                            edges=edges,
                            pattern_id=f"square_{square_count}",
                            significance_score=1.0,
                            frequency=1
                        )
                        squares.append(motif)
                        
                        if len(squares) >= 5000:  # Limit for performance
                            break
            except:
                # Fallback: manual 4-cycle detection
                for nodes in itertools.combinations(graph.nodes(), 4):
                    if self._is_square(graph, nodes):
                        square_count += 1
                        edges = self._get_square_edges(graph, nodes)
                        
                        motif = MotifInstance(
                            motif_type="squares",
                            nodes=list(nodes),
                            edges=edges,
                            pattern_id=f"square_{square_count}",
                            significance_score=1.0,
                            frequency=1
                        )
                        squares.append(motif)
                        
                        if len(squares) >= 1000:  # Lower limit for manual detection
                            break
            
            logger.info(f"Detected {len(squares)} squares")
            return squares
            
        except Exception as e:
            logger.error(f"Square detection failed: {e}")
            return []
    
    def _detect_wedges(self, graph: nx.Graph, min_frequency: int) -> List[MotifInstance]:
        """Detect wedge motifs (2-paths)"""
        try:
            wedges = []
            wedge_count = 0
            
            # Find all nodes with degree >= 2
            for center in graph.nodes():
                neighbors = list(graph.neighbors(center))
                
                # Create wedges from all pairs of neighbors
                for i in range(len(neighbors)):
                    for j in range(i+1, len(neighbors)):
                        if not graph.has_edge(neighbors[i], neighbors[j]):
                            wedge_count += 1
                            nodes = [neighbors[i], center, neighbors[j]]
                            edges = [(neighbors[i], center), (center, neighbors[j])]
                            
                            motif = MotifInstance(
                                motif_type="wedges",
                                nodes=nodes,
                                edges=edges,
                                pattern_id=f"wedge_{wedge_count}",
                                significance_score=1.0,
                                frequency=1
                            )
                            wedges.append(motif)
                            
                            if len(wedges) >= 20000:  # Limit for performance
                                break
                    
                    if len(wedges) >= 20000:
                        break
                
                if len(wedges) >= 20000:
                    break
            
            logger.info(f"Detected {len(wedges)} wedges")
            return wedges
            
        except Exception as e:
            logger.error(f"Wedge detection failed: {e}")
            return []
    
    def _detect_feed_forward_loops(self, graph: nx.Graph, min_frequency: int) -> List[MotifInstance]:
        """Detect feed-forward loop motifs (directed triangles with specific pattern)"""
        try:
            if not graph.is_directed():
                logger.warning("Feed-forward loops require directed graph")
                return []
            
            ffls = []
            ffl_count = 0
            
            # Find all directed triangles
            for triangle in nx.enumerate_all_cliques(graph.to_undirected()):
                if len(triangle) == 3:
                    nodes = list(triangle)
                    
                    # Check if it's a feed-forward loop pattern
                    if self._is_feed_forward_loop(graph, nodes):
                        ffl_count += 1
                        edges = self._get_directed_triangle_edges(graph, nodes)
                        
                        motif = MotifInstance(
                            motif_type="feed_forward_loops",
                            nodes=nodes,
                            edges=edges,
                            pattern_id=f"ffl_{ffl_count}",
                            significance_score=1.0,
                            frequency=1
                        )
                        ffls.append(motif)
                        
                        if len(ffls) >= 5000:  # Limit for performance
                            break
            
            logger.info(f"Detected {len(ffls)} feed-forward loops")
            return ffls
            
        except Exception as e:
            logger.error(f"Feed-forward loop detection failed: {e}")
            return []
    
    def _detect_bi_fans(self, graph: nx.Graph, min_frequency: int) -> List[MotifInstance]:
        """Detect bi-fan motifs (bipartite complete subgraphs K2,2)"""
        try:
            bi_fans = []
            bi_fan_count = 0
            
            # Find all 4-node combinations
            for nodes in itertools.combinations(graph.nodes(), 4):
                if self._is_bi_fan(graph, nodes):
                    bi_fan_count += 1
                    edges = self._get_bi_fan_edges(graph, nodes)
                    
                    motif = MotifInstance(
                        motif_type="bi_fans",
                        nodes=list(nodes),
                        edges=edges,
                        pattern_id=f"bi_fan_{bi_fan_count}",
                        significance_score=1.0,
                        frequency=1
                    )
                    bi_fans.append(motif)
                    
                    if len(bi_fans) >= 3000:  # Limit for performance
                        break
            
            logger.info(f"Detected {len(bi_fans)} bi-fans")
            return bi_fans
            
        except Exception as e:
            logger.error(f"Bi-fan detection failed: {e}")
            return []
    
    def _detect_chains(self, graph: nx.Graph, chain_length: int, min_frequency: int) -> List[MotifInstance]:
        """Detect chain motifs (paths of specified length)"""
        try:
            chains = []
            chain_count = 0
            
            # Find all simple paths of specified length
            for source in graph.nodes():
                for target in graph.nodes():
                    if source != target:
                        try:
                            paths = list(nx.all_simple_paths(graph, source, target, cutoff=chain_length-1))
                            for path in paths:
                                if len(path) == chain_length:
                                    chain_count += 1
                                    edges = [(path[i], path[i+1]) for i in range(len(path)-1)]
                                    
                                    motif = MotifInstance(
                                        motif_type=f"{chain_length}_chains",
                                        nodes=path,
                                        edges=edges,
                                        pattern_id=f"chain_{chain_length}_{chain_count}",
                                        significance_score=1.0,
                                        frequency=1
                                    )
                                    chains.append(motif)
                                    
                                    if len(chains) >= 15000:  # Limit for performance
                                        break
                        except:
                            continue
                    
                    if len(chains) >= 15000:
                        break
                
                if len(chains) >= 15000:
                    break
            
            logger.info(f"Detected {len(chains)} {chain_length}-chains")
            return chains
            
        except Exception as e:
            logger.error(f"Chain detection failed: {e}")
            return []
    
    def _detect_cliques(self, graph: nx.Graph, motif_sizes: List[int], min_frequency: int) -> List[MotifInstance]:
        """Detect clique motifs of various sizes"""
        try:
            cliques = []
            clique_count = 0
            
            for clique in nx.enumerate_all_cliques(graph):
                if len(clique) in motif_sizes:
                    clique_count += 1
                    nodes = list(clique)
                    edges = [(nodes[i], nodes[j]) for i in range(len(nodes)) 
                            for j in range(i+1, len(nodes)) 
                            if graph.has_edge(nodes[i], nodes[j])]
                    
                    motif = MotifInstance(
                        motif_type="cliques",
                        nodes=nodes,
                        edges=edges,
                        pattern_id=f"clique_{len(nodes)}_{clique_count}",
                        significance_score=1.0,
                        frequency=1
                    )
                    cliques.append(motif)
                    
                    if len(cliques) >= 5000:  # Limit for performance
                        break
            
            logger.info(f"Detected {len(cliques)} cliques")
            return cliques
            
        except Exception as e:
            logger.error(f"Clique detection failed: {e}")
            return []
    
    # Helper methods for specific motif patterns
    def _is_square(self, graph: nx.Graph, nodes: Tuple[str, ...]) -> bool:
        """Check if four nodes form a square (4-cycle)"""
        edges_present = 0
        for i in range(4):
            if graph.has_edge(nodes[i], nodes[(i+1) % 4]):
                edges_present += 1
        return edges_present == 4
    
    def _get_square_edges(self, graph: nx.Graph, nodes: Tuple[str, ...]) -> List[Tuple[str, str]]:
        """Get edges for a square motif"""
        edges = []
        for i in range(4):
            if graph.has_edge(nodes[i], nodes[(i+1) % 4]):
                edges.append((nodes[i], nodes[(i+1) % 4]))
        return edges
    
    def _is_feed_forward_loop(self, graph: nx.Graph, nodes: List[str]) -> bool:
        """Check if three nodes form a feed-forward loop pattern"""
        # A feed-forward loop has one node that regulates two others,
        # and one of those also regulates the third
        for i in range(3):
            for j in range(3):
                for k in range(3):
                    if i != j and j != k and i != k:
                        if (graph.has_edge(nodes[i], nodes[j]) and 
                            graph.has_edge(nodes[i], nodes[k]) and 
                            graph.has_edge(nodes[j], nodes[k])):
                            return True
        return False
    
    def _get_directed_triangle_edges(self, graph: nx.Graph, nodes: List[str]) -> List[Tuple[str, str]]:
        """Get edges for a directed triangle"""
        edges = []
        for i in range(3):
            for j in range(3):
                if i != j and graph.has_edge(nodes[i], nodes[j]):
                    edges.append((nodes[i], nodes[j]))
        return edges
    
    def _is_bi_fan(self, graph: nx.Graph, nodes: Tuple[str, ...]) -> bool:
        """Check if four nodes form a bi-fan (K2,2 bipartite graph)"""
        # Try all possible bipartitions
        for i in range(4):
            for j in range(i+1, 4):
                set1 = [nodes[i], nodes[j]]
                set2 = [nodes[k] for k in range(4) if k != i and k != j]
                
                # Check if it's a complete bipartite graph
                edge_count = 0
                for node1 in set1:
                    for node2 in set2:
                        if graph.has_edge(node1, node2):
                            edge_count += 1
                
                # Should have exactly 4 edges (2x2) and no internal edges
                internal_edges = sum(1 for n1, n2 in itertools.combinations(set1 + set2, 2)
                                   if graph.has_edge(n1, n2) and 
                                   ((n1 in set1 and n2 in set1) or (n1 in set2 and n2 in set2)))
                
                if edge_count == 4 and internal_edges == 0:
                    return True
        
        return False
    
    def _get_bi_fan_edges(self, graph: nx.Graph, nodes: Tuple[str, ...]) -> List[Tuple[str, str]]:
        """Get edges for a bi-fan motif"""
        edges = []
        for i in range(4):
            for j in range(i+1, 4):
                if graph.has_edge(nodes[i], nodes[j]):
                    edges.append((nodes[i], nodes[j]))
        return edges