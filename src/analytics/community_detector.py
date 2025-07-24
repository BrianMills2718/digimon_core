#!/usr/bin/env python3
"""
Community Detector - Advanced community detection for academic knowledge graphs

Implements Louvain, Leiden, and label propagation algorithms for discovering
research communities and thematic clusters with comprehensive error handling.
"""

import asyncio
import time
import logging
import networkx as nx
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime
from collections import defaultdict, Counter

# Import community detection algorithms
try:
    import networkx.algorithms.community as nx_community
    from networkx.algorithms.community import louvain_communities, label_propagation_communities
except ImportError:
    logger.warning("Advanced community detection modules not available")

from .graph_centrality_analyzer import AnalyticsError

logger = logging.getLogger(__name__)


class CommunityDetector:
    """Advanced community detection for academic knowledge graphs"""
    
    def __init__(self, neo4j_manager, distributed_tx_manager):
        self.neo4j_manager = neo4j_manager
        self.dtm = distributed_tx_manager
        self.community_cache = {}
        
        # Performance thresholds
        self.max_nodes_for_exact = 10000
        self.min_community_size = 3
        self.max_communities = 100
        
        # Algorithm configurations
        self.community_algorithms = {
            'louvain': self._louvain_clustering,
            'leiden': self._leiden_clustering,
            'label_propagation': self._label_propagation_clustering,
            'greedy_modularity': self._greedy_modularity_clustering
        }
        
        logger.info("CommunityDetector initialized")
    
    async def detect_research_communities(self, algorithm: str = 'louvain', 
                                        entity_types: List[str] = None,
                                        min_community_size: int = 5,
                                        resolution: float = 1.0,
                                        max_communities: int = 50) -> Dict[str, Any]:
        """Detect research communities using specified algorithm"""
        
        tx_id = f"community_detection_{algorithm}_{int(time.time())}"
        logger.info(f"Starting community detection - algorithm: {algorithm}, tx_id: {tx_id}")
        
        try:
            await self.dtm.begin_distributed_transaction(tx_id)
            
            # Build collaboration/citation network
            network_data = await self._build_research_network(entity_types)
            
            if not network_data or not network_data.get('edges'):
                logger.warning("No network data found for community detection")
                await self.dtm.commit_distributed_transaction(tx_id)
                return {
                    'algorithm': algorithm,
                    'communities': [],
                    'analysis': {},
                    'metadata': {
                        'total_communities': 0,
                        'total_nodes': 0,
                        'total_edges': 0,
                        'execution_time': 0
                    }
                }
            
            # Apply selected community detection algorithm
            start_time = time.time()
            communities = await self.community_algorithms[algorithm](
                network_data, min_community_size, resolution
            )
            execution_time = time.time() - start_time
            
            # Filter communities by size
            filtered_communities = [
                comm for comm in communities 
                if len(comm['members']) >= min_community_size
            ][:max_communities]
            
            # Analyze community characteristics
            community_analysis = await self._analyze_communities(filtered_communities, network_data)
            
            # Store results with provenance tracking
            await self._store_community_results(tx_id, filtered_communities, community_analysis)
            
            await self.dtm.commit_distributed_transaction(tx_id)
            
            result = {
                'algorithm': algorithm,
                'communities': filtered_communities,
                'analysis': community_analysis,
                'metadata': {
                    'total_communities': len(filtered_communities),
                    'total_nodes': len(network_data.get('nodes', {})),
                    'total_edges': len(network_data.get('edges', [])),
                    'largest_community_size': max(len(c['members']) for c in filtered_communities) if filtered_communities else 0,
                    'modularity_score': community_analysis.get('modularity', 0),
                    'clustering_coefficient': community_analysis.get('clustering', 0),
                    'execution_time': execution_time,
                    'min_community_size': min_community_size,
                    'resolution': resolution
                }
            }
            
            logger.info(f"Community detection completed - found {len(filtered_communities)} communities in {execution_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Community detection failed: {e}", exc_info=True)
            await self.dtm.rollback_distributed_transaction(tx_id)
            raise AnalyticsError(f"Community detection failed: {e}")
    
    async def _build_research_network(self, entity_types: List[str] = None) -> Dict[str, Any]:
        """Build collaboration/citation network for community detection"""
        
        logger.info("Building research network for community detection")
        
        # Build query based on entity types
        if entity_types:
            type_filter = "WHERE any(label IN labels(a) WHERE label IN $entity_types)"
            params = {'entity_types': entity_types}
        else:
            type_filter = ""
            params = {}
        
        # Query for network structure with weights
        query = f"""
        MATCH (a)-[r]-(b)
        {type_filter}
        RETURN DISTINCT 
            id(a) as node_a, 
            id(b) as node_b,
            labels(a) as labels_a,
            labels(b) as labels_b,
            a.name as name_a,
            b.name as name_b,
            type(r) as relationship_type,
            count(r) as edge_weight,
            collect(r.confidence) as confidences
        LIMIT 50000
        """
        
        await self.dtm.add_operation(self.dtm.current_tx_id, 'read', 'neo4j', 'network_data', {
            'query': query,
            'params': params,
            'operation_type': 'community_network_fetch'
        })
        
        network_data = await self.neo4j_manager.execute_read_query(query, params)
        
        # Process network data into structured format
        nodes = {}
        edges = []
        
        for record in network_data:
            node_a_id = record['node_a']
            node_b_id = record['node_b']
            
            # Add nodes with metadata
            if node_a_id not in nodes:
                nodes[node_a_id] = {
                    'id': node_a_id,
                    'name': record['name_a'] or f'Entity_{node_a_id}',
                    'labels': record['labels_a'],
                    'degree': 0
                }
            
            if node_b_id not in nodes:
                nodes[node_b_id] = {
                    'id': node_b_id,
                    'name': record['name_b'] or f'Entity_{node_b_id}',
                    'labels': record['labels_b'],
                    'degree': 0
                }
            
            # Calculate edge weight
            edge_weight = record['edge_weight']
            confidences = [c for c in record['confidences'] if c is not None]
            avg_confidence = np.mean(confidences) if confidences else 0.5
            
            final_weight = edge_weight * avg_confidence
            
            edges.append({
                'source': node_a_id,
                'target': node_b_id,
                'weight': final_weight,
                'relationship_type': record['relationship_type'],
                'edge_count': edge_weight,
                'avg_confidence': avg_confidence
            })
            
            # Update node degrees
            nodes[node_a_id]['degree'] += 1
            nodes[node_b_id]['degree'] += 1
        
        logger.info(f"Built network with {len(nodes)} nodes and {len(edges)} edges")
        
        return {
            'nodes': nodes,
            'edges': edges
        }
    
    async def _louvain_clustering(self, network_data: Dict, min_size: int, 
                                resolution: float) -> List[Dict]:
        """Louvain algorithm for community detection"""
        
        logger.info("Applying Louvain community detection algorithm")
        
        G = self._build_networkx_graph(network_data)
        
        try:
            # Apply Louvain algorithm
            communities = louvain_communities(G, resolution=resolution, weight='weight')
            
            # Convert to structured format
            structured_communities = []
            for i, community in enumerate(communities):
                if len(community) >= min_size:
                    community_data = await self._enrich_community_data(
                        community_id=i,
                        members=list(community),
                        algorithm='louvain',
                        network_data=network_data
                    )
                    structured_communities.append(community_data)
            
            logger.info(f"Louvain found {len(structured_communities)} communities (min_size >= {min_size})")
            return structured_communities
            
        except Exception as e:
            logger.error(f"Louvain clustering failed: {e}")
            # Fallback to greedy modularity
            return await self._greedy_modularity_clustering(network_data, min_size, resolution)
    
    async def _leiden_clustering(self, network_data: Dict, min_size: int, 
                               resolution: float) -> List[Dict]:
        """Leiden algorithm for community detection (fallback to Louvain)"""
        
        logger.info("Leiden algorithm not available, falling back to Louvain")
        return await self._louvain_clustering(network_data, min_size, resolution)
    
    async def _label_propagation_clustering(self, network_data: Dict, min_size: int, 
                                          resolution: float) -> List[Dict]:
        """Label propagation algorithm for community detection"""
        
        logger.info("Applying label propagation community detection algorithm")
        
        G = self._build_networkx_graph(network_data)
        
        try:
            # Apply label propagation
            communities = label_propagation_communities(G)
            
            # Convert to structured format
            structured_communities = []
            for i, community in enumerate(communities):
                if len(community) >= min_size:
                    community_data = await self._enrich_community_data(
                        community_id=i,
                        members=list(community),
                        algorithm='label_propagation',
                        network_data=network_data
                    )
                    structured_communities.append(community_data)
            
            logger.info(f"Label propagation found {len(structured_communities)} communities (min_size >= {min_size})")
            return structured_communities
            
        except Exception as e:
            logger.error(f"Label propagation clustering failed: {e}")
            # Fallback to greedy modularity
            return await self._greedy_modularity_clustering(network_data, min_size, resolution)
    
    async def _greedy_modularity_clustering(self, network_data: Dict, min_size: int, 
                                          resolution: float) -> List[Dict]:
        """Greedy modularity optimization for community detection"""
        
        logger.info("Applying greedy modularity community detection algorithm")
        
        G = self._build_networkx_graph(network_data)
        
        try:
            # Apply greedy modularity maximization
            communities = nx_community.greedy_modularity_communities(G, weight='weight')
            
            # Convert to structured format
            structured_communities = []
            for i, community in enumerate(communities):
                if len(community) >= min_size:
                    community_data = await self._enrich_community_data(
                        community_id=i,
                        members=list(community),
                        algorithm='greedy_modularity',
                        network_data=network_data
                    )
                    structured_communities.append(community_data)
            
            logger.info(f"Greedy modularity found {len(structured_communities)} communities (min_size >= {min_size})")
            return structured_communities
            
        except Exception as e:
            logger.error(f"Greedy modularity clustering failed: {e}")
            raise AnalyticsError(f"All community detection algorithms failed: {e}")
    
    def _build_networkx_graph(self, network_data: Dict) -> nx.Graph:
        """Build NetworkX graph from network data"""
        
        G = nx.Graph()
        
        # Add nodes with attributes
        for node_id, node_data in network_data['nodes'].items():
            G.add_node(node_id, **node_data)
        
        # Add edges with weights
        for edge in network_data['edges']:
            G.add_edge(
                edge['source'], 
                edge['target'], 
                weight=edge['weight'],
                relationship_type=edge['relationship_type']
            )
        
        return G
    
    async def _enrich_community_data(self, community_id: int, members: List[int], 
                                   algorithm: str, network_data: Dict) -> Dict[str, Any]:
        """Enrich community data with metadata and analysis"""
        
        # Get member names and metadata
        member_data = []
        labels_counter = Counter()
        
        for member_id in members:
            node_data = network_data['nodes'].get(member_id, {})
            member_data.append({
                'id': member_id,
                'name': node_data.get('name', f'Entity_{member_id}'),
                'labels': node_data.get('labels', []),
                'degree': node_data.get('degree', 0)
            })
            
            # Count labels for community characterization
            for label in node_data.get('labels', []):
                labels_counter[label] += 1
        
        # Calculate internal connectivity
        internal_edges = [
            edge for edge in network_data['edges']
            if edge['source'] in members and edge['target'] in members
        ]
        
        # Calculate external connectivity
        external_edges = [
            edge for edge in network_data['edges']
            if (edge['source'] in members) != (edge['target'] in members)
        ]
        
        # Community theme analysis
        dominant_labels = labels_counter.most_common(3)
        
        return {
            'id': community_id,
            'algorithm': algorithm,
            'members': member_data,
            'size': len(members),
            'internal_edges': len(internal_edges),
            'external_edges': len(external_edges),
            'density': len(internal_edges) / (len(members) * (len(members) - 1) / 2) if len(members) > 1 else 0,
            'dominant_labels': dominant_labels,
            'avg_degree': np.mean([m['degree'] for m in member_data]) if member_data else 0,
            'total_internal_weight': sum(e['weight'] for e in internal_edges),
            'total_external_weight': sum(e['weight'] for e in external_edges)
        }
    
    async def _analyze_communities(self, communities: List[Dict], 
                                 network_data: Dict) -> Dict[str, Any]:
        """Analyze community characteristics and research themes"""
        
        logger.info("Analyzing community characteristics")
        
        analysis = {
            'community_themes': {},
            'cross_community_connections': {},
            'size_distribution': {},
            'research_impact_metrics': {},
            'modularity': 0.0,
            'clustering': 0.0
        }
        
        if not communities:
            return analysis
        
        # Build graph for modularity calculation
        G = self._build_networkx_graph(network_data)
        
        # Create partition for modularity calculation
        partition = {}
        for i, community in enumerate(communities):
            for member in community['members']:
                partition[member['id']] = i
        
        # Calculate modularity
        try:
            analysis['modularity'] = nx_community.modularity(G, [
                set(member['id'] for member in comm['members']) 
                for comm in communities
            ], weight='weight')
        except:
            analysis['modularity'] = 0.0
        
        # Calculate clustering coefficient
        try:
            analysis['clustering'] = nx.average_clustering(G, weight='weight')
        except:
            analysis['clustering'] = 0.0
        
        # Analyze each community
        for community in communities:
            community_id = community['id']
            
            # Extract research themes
            themes = await self._extract_community_themes(community)
            analysis['community_themes'][community_id] = themes
            
            # Calculate community-specific metrics
            impact_metrics = await self._calculate_community_impact(community)
            analysis['research_impact_metrics'][community_id] = impact_metrics
        
        # Analyze cross-community connections
        analysis['cross_community_connections'] = await self._analyze_cross_community_links(
            communities, network_data
        )
        
        # Size distribution analysis
        sizes = [comm['size'] for comm in communities]
        analysis['size_distribution'] = {
            'mean': np.mean(sizes),
            'std': np.std(sizes),
            'min': min(sizes),
            'max': max(sizes),
            'median': np.median(sizes)
        }
        
        return analysis
    
    async def _extract_community_themes(self, community: Dict) -> Dict[str, Any]:
        """Extract research themes from community members"""
        
        # Analyze dominant labels
        label_counts = Counter()
        for member in community['members']:
            for label in member.get('labels', []):
                label_counts[label] += 1
        
        # Get top themes based on labels
        top_themes = label_counts.most_common(5)
        
        # Calculate theme coherence
        total_members = len(community['members'])
        theme_coherence = {}
        
        for theme, count in top_themes:
            coherence = count / total_members
            theme_coherence[theme] = coherence
        
        return {
            'dominant_themes': top_themes,
            'theme_coherence': theme_coherence,
            'diversity_score': len(label_counts) / total_members if total_members > 0 else 0
        }
    
    async def _calculate_community_impact(self, community: Dict) -> Dict[str, Any]:
        """Calculate research impact metrics for a community"""
        
        # Basic structural metrics
        size = community['size']
        density = community['density']
        internal_strength = community['total_internal_weight']
        external_strength = community['total_external_weight']
        
        # Calculate cohesion score
        cohesion = internal_strength / (internal_strength + external_strength) if (internal_strength + external_strength) > 0 else 0
        
        # Calculate influence score (based on external connections)
        influence = external_strength / size if size > 0 else 0
        
        # Calculate activity score (based on average degree)
        activity = community['avg_degree']
        
        return {
            'cohesion_score': cohesion,
            'influence_score': influence,
            'activity_score': activity,
            'size_impact': size,
            'density_score': density,
            'internal_strength': internal_strength,
            'external_strength': external_strength
        }
    
    async def _analyze_cross_community_links(self, communities: List[Dict], 
                                           network_data: Dict) -> Dict[str, Any]:
        """Analyze connections between communities"""
        
        # Create community membership mapping
        member_to_community = {}
        for i, community in enumerate(communities):
            for member in community['members']:
                member_to_community[member['id']] = i
        
        # Analyze cross-community edges
        cross_community_edges = []
        community_connections = defaultdict(lambda: defaultdict(float))
        
        for edge in network_data['edges']:
            source_comm = member_to_community.get(edge['source'])
            target_comm = member_to_community.get(edge['target'])
            
            if source_comm is not None and target_comm is not None and source_comm != target_comm:
                cross_community_edges.append({
                    'source_community': source_comm,
                    'target_community': target_comm,
                    'weight': edge['weight'],
                    'relationship_type': edge['relationship_type']
                })
                community_connections[source_comm][target_comm] += edge['weight']
                community_connections[target_comm][source_comm] += edge['weight']
        
        # Find strongest inter-community connections
        strongest_connections = []
        for source_comm, targets in community_connections.items():
            for target_comm, weight in targets.items():
                if source_comm < target_comm:  # Avoid duplicates
                    strongest_connections.append({
                        'community_1': source_comm,
                        'community_2': target_comm,
                        'connection_strength': weight
                    })
        
        strongest_connections.sort(key=lambda x: x['connection_strength'], reverse=True)
        
        return {
            'total_cross_community_edges': len(cross_community_edges),
            'community_connections': dict(community_connections),
            'strongest_connections': strongest_connections[:10]  # Top 10
        }
    
    async def _store_community_results(self, tx_id: str, communities: List[Dict], 
                                     analysis: Dict[str, Any]) -> None:
        """Store community detection results with provenance"""
        
        # Add storage operation to distributed transaction
        await self.dtm.add_operation(tx_id, 'write', 'neo4j', 'community_results', {
            'communities': communities,
            'analysis': analysis,
            'operation_type': 'community_detection_storage',
            'timestamp': datetime.now().isoformat()
        })
        
        logger.info(f"Community detection results prepared for storage - {len(communities)} communities")