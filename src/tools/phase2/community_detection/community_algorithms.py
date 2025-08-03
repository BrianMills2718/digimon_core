"""Community Detection Algorithms

Implements various community detection algorithms.
"""

import networkx as nx
import numpy as np
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
import random

try:
    import community as louvain_community
except ImportError:
    louvain_community = None

try:
    import leidenalg
    import igraph as ig
except ImportError:
    leidenalg = None
    ig = None

from .community_data_models import CommunityAlgorithm, CommunityResult, CommunityConfig
from src.core.logging_config import get_logger

logger = get_logger(__name__)


class CommunityDetector:
    """Detect communities using various algorithms"""
    
    def __init__(self):
        self.community_configs = CommunityConfig.get_default_configs()
    
    def detect_communities(self, graph: nx.Graph, algorithm: CommunityAlgorithm, 
                          config: Optional[Dict[str, Any]] = None) -> CommunityResult:
        """Detect communities using a specific algorithm"""
        try:
            start_time = time.time()
            
            # Get configuration
            base_config = self.community_configs.get(algorithm, 
                                                   CommunityConfig.get_default_configs()[algorithm])
            if config:
                # Update config with provided parameters
                for key, value in config.items():
                    if hasattr(base_config, key):
                        setattr(base_config, key, value)
            
            # Prepare graph for this algorithm
            prepared_graph = self._prepare_graph_for_algorithm(graph, algorithm, base_config)
            
            # Detect communities
            if algorithm == CommunityAlgorithm.LOUVAIN:
                communities = self._louvain_communities(prepared_graph, base_config)
            elif algorithm == CommunityAlgorithm.LEIDEN:
                communities = self._leiden_communities(prepared_graph, base_config)
            elif algorithm == CommunityAlgorithm.LABEL_PROPAGATION:
                communities = self._label_propagation_communities(prepared_graph, base_config)
            elif algorithm == CommunityAlgorithm.GREEDY_MODULARITY:
                communities = self._greedy_modularity_communities(prepared_graph, base_config)
            elif algorithm == CommunityAlgorithm.FLUID_COMMUNITIES:
                communities = self._fluid_communities(prepared_graph, base_config)
            elif algorithm == CommunityAlgorithm.GIRVAN_NEWMAN:
                communities = self._girvan_newman_communities(prepared_graph, base_config)
            else:
                raise ValueError(f"Unknown community detection algorithm: {algorithm}")
            
            # Filter communities by size if specified
            if base_config.min_community_size > 1 or base_config.max_community_size < 1000:
                communities = self._filter_communities_by_size(
                    communities, base_config.min_community_size, base_config.max_community_size
                )
            
            # Calculate quality metrics
            modularity = self._calculate_modularity(prepared_graph, communities)
            performance = self._calculate_performance(prepared_graph, communities)
            
            calculation_time = time.time() - start_time
            
            return CommunityResult(
                algorithm=algorithm.value,
                communities=communities,
                modularity=modularity,
                performance=performance,
                num_communities=len(set(communities.values())),
                calculation_time=calculation_time,
                metadata={
                    "config": base_config.__dict__,
                    "graph_nodes": len(prepared_graph.nodes),
                    "graph_edges": len(prepared_graph.edges),
                    "total_nodes_assigned": len(communities),
                    "calculated_at": datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"Community detection failed for {algorithm}: {e}")
            return CommunityResult(
                algorithm=algorithm.value,
                communities={},
                modularity=0.0,
                performance=0.0,
                num_communities=0,
                calculation_time=0.0,
                metadata={"error": str(e)}
            )
    
    def _prepare_graph_for_algorithm(self, graph: nx.Graph, algorithm: CommunityAlgorithm, 
                                    config: CommunityConfig) -> nx.Graph:
        """Prepare graph for specific algorithm"""
        prepared_graph = graph.copy()
        
        # Convert to undirected for most algorithms
        if prepared_graph.is_directed() and not config.directed:
            prepared_graph = prepared_graph.to_undirected()
        
        # Remove self-loops
        prepared_graph.remove_edges_from(nx.selfloop_edges(prepared_graph))
        
        # Ensure weight attributes
        for u, v, data in prepared_graph.edges(data=True):
            if config.weighted and config.weight_attribute not in data:
                data[config.weight_attribute] = 1.0
        
        return prepared_graph
    
    def _louvain_communities(self, graph: nx.Graph, config: CommunityConfig) -> Dict[str, int]:
        """Detect communities using Louvain algorithm"""
        try:
            if louvain_community is None:
                raise ImportError("python-louvain package not available")
            
            # Set random seed if specified
            if config.random_seed is not None:
                random.seed(config.random_seed)
                np.random.seed(config.random_seed)
            
            # Detect communities
            if config.weighted:
                partition = louvain_community.best_partition(
                    graph, 
                    weight=config.weight_attribute,
                    resolution=config.resolution,
                    randomize=config.random_seed is None
                )
            else:
                partition = louvain_community.best_partition(
                    graph,
                    resolution=config.resolution,
                    randomize=config.random_seed is None
                )
            
            logger.info(f"Louvain detected {len(set(partition.values()))} communities")
            return partition
            
        except ImportError as e:
            logger.warning(f"Louvain algorithm not available: {e}, using label propagation fallback")
            return self._label_propagation_communities(graph, config)
        except Exception as e:
            logger.error(f"Louvain algorithm failed: {e}")
            return {}
    
    def _leiden_communities(self, graph: nx.Graph, config: CommunityConfig) -> Dict[str, int]:
        """Detect communities using Leiden algorithm"""
        try:
            if leidenalg is None or ig is None:
                raise ImportError("leidenalg or python-igraph package not available")
            
            # Convert NetworkX graph to igraph
            edge_list = list(graph.edges())
            node_list = list(graph.nodes())
            
            # Create igraph
            ig_graph = ig.Graph()
            ig_graph.add_vertices(len(node_list))
            
            # Map node names to indices
            node_to_idx = {node: idx for idx, node in enumerate(node_list)}
            idx_edges = [(node_to_idx[u], node_to_idx[v]) for u, v in edge_list]
            ig_graph.add_edges(idx_edges)
            
            # Add weights if specified
            if config.weighted:
                weights = [graph[u][v].get(config.weight_attribute, 1.0) for u, v in edge_list]
                ig_graph.es['weight'] = weights
            
            # Run Leiden algorithm
            if config.weighted:
                partition = leidenalg.find_partition(
                    ig_graph, 
                    leidenalg.ModularityVertexPartition,
                    weights='weight',
                    resolution_parameter=config.resolution,
                    seed=config.random_seed
                )
            else:
                partition = leidenalg.find_partition(
                    ig_graph,
                    leidenalg.ModularityVertexPartition,
                    resolution_parameter=config.resolution,
                    seed=config.random_seed
                )
            
            # Convert back to NetworkX format
            communities = {}
            for community_id, community in enumerate(partition):
                for node_idx in community:
                    node_name = node_list[node_idx]
                    communities[node_name] = community_id
            
            logger.info(f"Leiden detected {len(partition)} communities")
            return communities
            
        except ImportError as e:
            logger.warning(f"Leiden algorithm not available: {e}, using Louvain fallback")
            return self._louvain_communities(graph, config)
        except Exception as e:
            logger.error(f"Leiden algorithm failed: {e}")
            return {}
    
    def _label_propagation_communities(self, graph: nx.Graph, config: CommunityConfig) -> Dict[str, int]:
        """Detect communities using label propagation algorithm"""
        try:
            # Set random seed if specified
            if config.random_seed is not None:
                random.seed(config.random_seed)
                np.random.seed(config.random_seed)
            
            # Use NetworkX label propagation
            if config.weighted:
                communities_generator = nx.algorithms.community.label_propagation_communities(
                    graph, weight=config.weight_attribute, seed=config.random_seed
                )
            else:
                communities_generator = nx.algorithms.community.label_propagation_communities(
                    graph, seed=config.random_seed
                )
            
            # Convert to node -> community_id mapping
            communities = {}
            for community_id, community_nodes in enumerate(communities_generator):
                for node in community_nodes:
                    communities[node] = community_id
            
            logger.info(f"Label propagation detected {len(set(communities.values()))} communities")
            return communities
            
        except Exception as e:
            logger.error(f"Label propagation algorithm failed: {e}")
            return {}
    
    def _greedy_modularity_communities(self, graph: nx.Graph, config: CommunityConfig) -> Dict[str, int]:
        """Detect communities using greedy modularity optimization"""
        try:
            # Use NetworkX greedy modularity communities
            if config.weighted:
                communities_generator = nx.algorithms.community.greedy_modularity_communities(
                    graph, weight=config.weight_attribute, resolution=config.resolution
                )
            else:
                communities_generator = nx.algorithms.community.greedy_modularity_communities(
                    graph, resolution=config.resolution
                )
            
            # Convert to node -> community_id mapping
            communities = {}
            for community_id, community_nodes in enumerate(communities_generator):
                for node in community_nodes:
                    communities[node] = community_id
            
            logger.info(f"Greedy modularity detected {len(set(communities.values()))} communities")
            return communities
            
        except Exception as e:
            logger.error(f"Greedy modularity algorithm failed: {e}")
            return {}
    
    def _fluid_communities(self, graph: nx.Graph, config: CommunityConfig) -> Dict[str, int]:
        """Detect communities using fluid communities algorithm"""
        try:
            # Estimate number of communities (fluid communities requires this)
            estimated_k = max(2, min(10, len(graph.nodes) // 20))
            
            # Set random seed if specified
            if config.random_seed is not None:
                random.seed(config.random_seed)
                np.random.seed(config.random_seed)
            
            # Use NetworkX fluid communities
            communities_generator = nx.algorithms.community.asyn_fluidc(
                graph, k=estimated_k, max_iter=config.max_iterations, seed=config.random_seed
            )
            
            # Convert to node -> community_id mapping
            communities = {}
            for community_id, community_nodes in enumerate(communities_generator):
                for node in community_nodes:
                    communities[node] = community_id
            
            logger.info(f"Fluid communities detected {len(set(communities.values()))} communities")
            return communities
            
        except Exception as e:
            logger.error(f"Fluid communities algorithm failed: {e}")
            return {}
    
    def _girvan_newman_communities(self, graph: nx.Graph, config: CommunityConfig) -> Dict[str, int]:
        """Detect communities using Girvan-Newman algorithm"""
        try:
            # This is computationally expensive, limit to small graphs
            if len(graph.nodes) > 100:
                logger.warning("Girvan-Newman algorithm is expensive, limiting to largest connected component")
                largest_cc = max(nx.connected_components(graph), key=len)
                graph = graph.subgraph(largest_cc).copy()
            
            # Use NetworkX Girvan-Newman
            communities_generator = nx.algorithms.community.girvan_newman(graph)
            
            # Get first few levels of the dendrogram
            communities = {}
            best_modularity = -1
            best_partition = None
            
            for level, partition in enumerate(communities_generator):
                if level >= config.max_iterations:
                    break
                
                # Convert to communities dict
                current_communities = {}
                for community_id, community_nodes in enumerate(partition):
                    for node in community_nodes:
                        current_communities[node] = community_id
                
                # Calculate modularity for this partition
                modularity = self._calculate_modularity(graph, current_communities)
                
                if modularity > best_modularity:
                    best_modularity = modularity
                    best_partition = current_communities
            
            if best_partition:
                communities = best_partition
                logger.info(f"Girvan-Newman detected {len(set(communities.values()))} communities")
            else:
                # Fallback: each node is its own community
                communities = {node: i for i, node in enumerate(graph.nodes)}
                logger.warning("Girvan-Newman failed, using trivial partition")
            
            return communities
            
        except Exception as e:
            logger.error(f"Girvan-Newman algorithm failed: {e}")
            return {}
    
    def _filter_communities_by_size(self, communities: Dict[str, int], 
                                   min_size: int, max_size: int) -> Dict[str, int]:
        """Filter communities by size constraints"""
        try:
            # Count community sizes
            community_sizes = {}
            for node, community_id in communities.items():
                community_sizes[community_id] = community_sizes.get(community_id, 0) + 1
            
            # Identify communities within size constraints
            valid_communities = {
                community_id: size for community_id, size in community_sizes.items()
                if min_size <= size <= max_size
            }
            
            # Filter nodes
            filtered_communities = {
                node: community_id for node, community_id in communities.items()
                if community_id in valid_communities
            }
            
            # Reassign community IDs to be consecutive
            old_to_new_id = {old_id: new_id for new_id, old_id in enumerate(valid_communities.keys())}
            final_communities = {
                node: old_to_new_id[community_id] 
                for node, community_id in filtered_communities.items()
            }
            
            removed_nodes = len(communities) - len(final_communities)
            if removed_nodes > 0:
                logger.info(f"Filtered out {removed_nodes} nodes in communities outside size constraints")
            
            return final_communities
            
        except Exception as e:
            logger.error(f"Community filtering failed: {e}")
            return communities
    
    def _calculate_modularity(self, graph: nx.Graph, communities: Dict[str, int]) -> float:
        """Calculate modularity of community partition"""
        try:
            if not communities:
                return 0.0
            
            # Convert communities dict to list of sets format
            community_sets = {}
            for node, community_id in communities.items():
                if community_id not in community_sets:
                    community_sets[community_id] = set()
                community_sets[community_id].add(node)
            
            community_list = list(community_sets.values())
            
            # Calculate modularity using NetworkX
            modularity = nx.algorithms.community.modularity(graph, community_list)
            return modularity
            
        except Exception as e:
            logger.error(f"Modularity calculation failed: {e}")
            return 0.0
    
    def _calculate_performance(self, graph: nx.Graph, communities: Dict[str, int]) -> float:
        """Calculate performance metric of community partition"""
        try:
            if not communities:
                return 0.0
            
            # Convert communities dict to list of sets format
            community_sets = {}
            for node, community_id in communities.items():
                if community_id not in community_sets:
                    community_sets[community_id] = set()
                community_sets[community_id].add(node)
            
            community_list = list(community_sets.values())
            
            # Calculate performance using NetworkX
            performance = nx.algorithms.community.performance(graph, community_list)
            return performance
            
        except Exception as e:
            logger.error(f"Performance calculation failed: {e}")
            return 0.0