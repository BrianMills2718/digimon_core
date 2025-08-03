#!/usr/bin/env python3
"""
Cross-Modal Entity Linker - Link entities across text, image, and structured data modalities

Implements multi-modal entity linking using embeddings and graph structure analysis
with comprehensive error handling and integration with the distributed transaction system.
"""

import asyncio
import time
import logging
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime
from collections import defaultdict
import json

from .graph_centrality_analyzer import AnalyticsError

logger = logging.getLogger(__name__)


class EntityResolver:
    """Entity resolution algorithm for cross-modal linking"""
    
    def __init__(self, similarity_matrices: Dict[str, np.ndarray], 
                 graph_contexts: Dict[str, Any],
                 similarity_threshold: float = 0.85,
                 modality_weights: Dict[str, float] = None):
        self.similarity_matrices = similarity_matrices
        self.graph_contexts = graph_contexts
        self.similarity_threshold = similarity_threshold
        self.modality_weights = modality_weights or {
            'text': 0.4, 'image': 0.3, 'structured': 0.3
        }
    
    async def resolve_entities(self) -> List[Dict[str, Any]]:
        """Resolve entities using similarity and graph context"""
        
        logger.info("Starting entity resolution")
        
        # Find high-confidence cross-modal matches
        cross_modal_matches = await self._find_cross_modal_matches()
        
        # Apply graph-based validation
        validated_matches = await self._validate_with_graph_context(cross_modal_matches)
        
        # Create entity clusters
        entity_clusters = await self._create_entity_clusters(validated_matches)
        
        logger.info(f"Resolved {len(entity_clusters)} entity clusters")
        return entity_clusters
    
    async def _find_cross_modal_matches(self) -> List[Dict[str, Any]]:
        """Find high-confidence matches across modalities"""
        
        matches = []
        
        # Compare each pair of modalities
        modalities = list(self.similarity_matrices.keys())
        
        for i, mod1 in enumerate(modalities):
            for j, mod2 in enumerate(modalities[i+1:], i+1):
                # Calculate cross-modal similarity
                sim_matrix = await self._calculate_cross_modal_similarity(mod1, mod2)
                
                # Find high-confidence matches
                high_conf_matches = await self._extract_high_confidence_matches(
                    sim_matrix, mod1, mod2
                )
                
                matches.extend(high_conf_matches)
        
        return matches
    
    async def _calculate_cross_modal_similarity(self, mod1: str, mod2: str) -> np.ndarray:
        """Calculate similarity matrix between two modalities"""
        
        emb1 = self.similarity_matrices[mod1]
        emb2 = self.similarity_matrices[mod2]
        
        # Cosine similarity
        norm1 = np.linalg.norm(emb1, axis=1)
        norm2 = np.linalg.norm(emb2, axis=1)
        
        similarity = np.dot(emb1, emb2.T) / np.outer(norm1, norm2)
        
        return similarity
    
    async def _extract_high_confidence_matches(self, sim_matrix: np.ndarray, 
                                             mod1: str, mod2: str) -> List[Dict[str, Any]]:
        """Extract high-confidence matches from similarity matrix"""
        
        matches = []
        
        # Find matches above threshold
        high_sim_indices = np.where(sim_matrix >= self.similarity_threshold)
        
        for i, j in zip(high_sim_indices[0], high_sim_indices[1]):
            match = {
                'modality_1': mod1,
                'modality_2': mod2,
                'entity_1_idx': i,
                'entity_2_idx': j,
                'similarity_score': sim_matrix[i, j],
                'confidence': sim_matrix[i, j]
            }
            matches.append(match)
        
        return matches
    
    async def _validate_with_graph_context(self, matches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate matches using graph context"""
        
        validated_matches = []
        
        for match in matches:
            # Get graph context for both entities
            entity1_context = self.graph_contexts.get(f"{match['modality_1']}_{match['entity_1_idx']}", {})
            entity2_context = self.graph_contexts.get(f"{match['modality_2']}_{match['entity_2_idx']}", {})
            
            # Calculate context similarity
            context_similarity = await self._calculate_context_similarity(
                entity1_context, entity2_context
            )
            
            # Adjust confidence based on context
            adjusted_confidence = (match['confidence'] + context_similarity) / 2
            
            if adjusted_confidence >= self.similarity_threshold * 0.8:  # Slightly lower threshold after context
                match['context_similarity'] = context_similarity
                match['adjusted_confidence'] = adjusted_confidence
                validated_matches.append(match)
        
        return validated_matches
    
    async def _calculate_context_similarity(self, context1: Dict, context2: Dict) -> float:
        """Calculate similarity between graph contexts"""
        
        # Compare connected entities
        conn1 = set(context1.get('connected_entities', []))
        conn2 = set(context2.get('connected_entities', []))
        
        if not conn1 and not conn2:
            return 0.5  # Neutral if no context
        
        if not conn1 or not conn2:
            return 0.1  # Low if only one has context
        
        # Jaccard similarity of connected entities
        intersection = len(conn1.intersection(conn2))
        union = len(conn1.union(conn2))
        
        jaccard_similarity = intersection / union if union > 0 else 0
        
        return jaccard_similarity
    
    async def _create_entity_clusters(self, validated_matches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create entity clusters from validated matches"""
        
        # Build graph of entity matches
        match_graph = defaultdict(set)
        
        for match in validated_matches:
            entity1_key = f"{match['modality_1']}_{match['entity_1_idx']}"
            entity2_key = f"{match['modality_2']}_{match['entity_2_idx']}"
            
            match_graph[entity1_key].add(entity2_key)
            match_graph[entity2_key].add(entity1_key)
        
        # Find connected components (entity clusters)
        visited = set()
        clusters = []
        
        for entity_key in match_graph:
            if entity_key not in visited:
                cluster = await self._dfs_cluster(entity_key, match_graph, visited)
                if len(cluster) > 1:  # Only multi-entity clusters
                    clusters.append(cluster)
        
        # Enrich clusters with metadata
        enriched_clusters = []
        for i, cluster in enumerate(clusters):
            enriched_cluster = await self._enrich_entity_cluster(i, cluster)
            enriched_clusters.append(enriched_cluster)
        
        return enriched_clusters
    
    async def _dfs_cluster(self, start_entity: str, match_graph: Dict, visited: Set[str]) -> List[str]:
        """DFS to find connected entity cluster"""
        
        cluster = []
        stack = [start_entity]
        
        while stack:
            entity = stack.pop()
            if entity not in visited:
                visited.add(entity)
                cluster.append(entity)
                
                # Add connected entities to stack
                for connected in match_graph[entity]:
                    if connected not in visited:
                        stack.append(connected)
        
        return cluster
    
    async def _enrich_entity_cluster(self, cluster_id: int, cluster: List[str]) -> Dict[str, Any]:
        """Enrich entity cluster with metadata"""
        
        # Parse cluster entities by modality
        modality_entities = defaultdict(list)
        
        for entity_key in cluster:
            modality, idx = entity_key.split('_', 1)
            modality_entities[modality].append(int(idx))
        
        return {
            'cluster_id': cluster_id,
            'entities': dict(modality_entities),
            'size': len(cluster),
            'modalities': list(modality_entities.keys()),
            'cross_modal_count': len(modality_entities)
        }


class CrossModalEntityLinker:
    """Link entities across text, image, and structured data modalities"""
    
    def __init__(self, neo4j_manager, distributed_tx_manager, embedding_service=None):
        self.neo4j_manager = neo4j_manager
        self.dtm = distributed_tx_manager
        
        # Use real embedding service if none provided
        if embedding_service is None:
            from .real_embedding_service import RealEmbeddingService
            self.embedding_service = RealEmbeddingService()
        else:
            self.embedding_service = embedding_service
        
        # Configuration
        self.similarity_threshold = 0.85
        self.modality_weights = {
            'text': 0.4,
            'image': 0.3,
            'structured': 0.3
        }
        self.max_entities_per_modality = 1000
        
        logger.info("CrossModalEntityLinker initialized")
    
    async def link_cross_modal_entities(self, entity_candidates: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """Link entities across different modalities using embeddings and graph structure"""
        
        tx_id = f"cross_modal_linking_{int(time.time())}"
        logger.info(f"Starting cross-modal entity linking - tx_id: {tx_id}")
        
        try:
            await self.dtm.begin_distributed_transaction(tx_id)
            
            # Validate and limit input
            filtered_candidates = await self._filter_entity_candidates(entity_candidates)
            
            if not filtered_candidates:
                logger.warning("No valid entity candidates found")
                await self.dtm.commit_distributed_transaction(tx_id)
                return {
                    'linked_entities': [],
                    'cross_modal_graph': {},
                    'linking_metrics': {'total_entities': 0, 'linked_entities': 0}
                }
            
            # Generate embeddings for all entity candidates
            modal_embeddings = await self._generate_modal_embeddings(filtered_candidates)
            
            # Calculate cross-modal similarity matrices
            similarity_matrices = await self._calculate_cross_modal_similarities(modal_embeddings)
            
            # Get graph context for entities
            graph_contexts = await self._get_graph_contexts(filtered_candidates)
            
            # Apply graph-based entity resolution
            linked_entities = await self._resolve_entities_with_graph_context(
                filtered_candidates, similarity_matrices, graph_contexts
            )
            
            # Create cross-modal entity graph
            cross_modal_graph = await self._build_cross_modal_graph(linked_entities)
            
            # Store results with full provenance
            await self._store_cross_modal_links(tx_id, linked_entities, cross_modal_graph)
            
            await self.dtm.commit_distributed_transaction(tx_id)
            
            result = {
                'linked_entities': linked_entities,
                'cross_modal_graph': cross_modal_graph,
                'linking_metrics': await self._calculate_linking_metrics(
                    filtered_candidates, linked_entities
                )
            }
            
            logger.info(f"Cross-modal entity linking completed - found {len(linked_entities)} entity clusters")
            return result
            
        except Exception as e:
            logger.error(f"Cross-modal entity linking failed: {e}", exc_info=True)
            await self.dtm.rollback_distributed_transaction(tx_id)
            raise AnalyticsError(f"Cross-modal entity linking failed: {e}")
    
    async def _filter_entity_candidates(self, entity_candidates: Dict[str, List[Dict]]) -> Dict[str, List[Dict]]:
        """Filter and validate entity candidates"""
        
        filtered = {}
        
        for modality, entities in entity_candidates.items():
            if modality in self.modality_weights:
                # Limit entities per modality for performance
                limited_entities = entities[:self.max_entities_per_modality]
                
                # Validate entity structure
                valid_entities = []
                for entity in limited_entities:
                    if await self._validate_entity(entity, modality):
                        valid_entities.append(entity)
                
                if valid_entities:
                    filtered[modality] = valid_entities
        
        return filtered
    
    async def _validate_entity(self, entity: Dict, modality: str) -> bool:
        """Validate entity structure based on modality"""
        
        if modality == 'text':
            return 'text_content' in entity and entity['text_content'].strip()
        elif modality == 'image':
            return 'image_path' in entity or 'image_data' in entity
        elif modality == 'structured':
            return 'structured_data' in entity and entity['structured_data']
        
        return False
    
    async def _generate_modal_embeddings(self, entity_candidates: Dict[str, List[Dict]]) -> Dict[str, np.ndarray]:
        """Generate embeddings for entities in each modality"""
        
        logger.info("Generating embeddings for all modalities")
        modal_embeddings = {}
        
        for modality, entities in entity_candidates.items():
            if modality == 'text':
                embeddings = await self.embedding_service.generate_text_embeddings([
                    entity['text_content'] for entity in entities
                ])
            elif modality == 'image':
                embeddings = await self.embedding_service.generate_image_embeddings([
                    entity.get('image_path', entity.get('image_data', '')) for entity in entities
                ])
            elif modality == 'structured':
                embeddings = await self.embedding_service.generate_structured_embeddings([
                    entity['structured_data'] for entity in entities
                ])
            else:
                logger.warning(f"Unknown modality: {modality}")
                continue
            
            modal_embeddings[modality] = embeddings
            logger.info(f"Generated {len(embeddings)} embeddings for {modality} modality")
        
        return modal_embeddings
    
    async def _calculate_cross_modal_similarities(self, modal_embeddings: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        """Calculate cross-modal similarity matrices"""
        
        logger.info("Calculating cross-modal similarity matrices")
        
        similarity_matrices = {}
        modalities = list(modal_embeddings.keys())
        
        for i, mod1 in enumerate(modalities):
            for j, mod2 in enumerate(modalities[i+1:], i+1):
                key = f"{mod1}_{mod2}"
                
                emb1 = modal_embeddings[mod1]
                emb2 = modal_embeddings[mod2]
                
                # Calculate cosine similarity matrix
                norm1 = np.linalg.norm(emb1, axis=1, keepdims=True)
                norm2 = np.linalg.norm(emb2, axis=1, keepdims=True)
                
                normalized_emb1 = emb1 / norm1
                normalized_emb2 = emb2 / norm2
                
                similarity_matrix = np.dot(normalized_emb1, normalized_emb2.T)
                similarity_matrices[key] = similarity_matrix
        
        # Store individual modality embeddings for resolver
        for modality, embeddings in modal_embeddings.items():
            similarity_matrices[modality] = embeddings
        
        return similarity_matrices
    
    async def _get_graph_contexts(self, entity_candidates: Dict[str, List[Dict]]) -> Dict[str, Dict]:
        """Get graph context for each entity candidate"""
        
        logger.info("Retrieving graph contexts for entity candidates")
        
        graph_contexts = {}
        
        for modality, entities in entity_candidates.items():
            for i, entity in enumerate(entities):
                entity_key = f"{modality}_{i}"
                
                # Query for connected entities based on entity ID or name
                context = await self._query_entity_context(entity, modality)
                graph_contexts[entity_key] = context
        
        return graph_contexts
    
    async def _query_entity_context(self, entity: Dict, modality: str) -> Dict[str, Any]:
        """Query graph context for a single entity"""
        
        try:
            # Determine entity identifier
            entity_id = entity.get('entity_id')
            entity_name = entity.get('name') or entity.get('title')
            
            if entity_id:
                query = """
                MATCH (e)-[r]-(connected)
                WHERE id(e) = $entity_id
                RETURN collect(DISTINCT id(connected)) as connected_entities,
                       collect(DISTINCT type(r)) as relationship_types
                LIMIT 100
                """
                params = {'entity_id': entity_id}
            elif entity_name:
                query = """
                MATCH (e)-[r]-(connected)
                WHERE e.name = $entity_name OR e.title = $entity_name
                RETURN collect(DISTINCT id(connected)) as connected_entities,
                       collect(DISTINCT type(r)) as relationship_types
                LIMIT 100
                """
                params = {'entity_name': entity_name}
            else:
                return {'connected_entities': [], 'relationship_types': []}
            
            await self.dtm.add_operation(self.dtm.current_tx_id, 'read', 'neo4j', 'entity_context', {
                'query': query,
                'params': params,
                'operation_type': 'cross_modal_context_fetch'
            })
            
            result = await self.neo4j_manager.execute_read_query(query, params)
            
            if result:
                return {
                    'connected_entities': result[0].get('connected_entities', []),
                    'relationship_types': result[0].get('relationship_types', [])
                }
            else:
                return {'connected_entities': [], 'relationship_types': []}
                
        except Exception as e:
            logger.warning(f"Failed to get context for entity: {e}")
            return {'connected_entities': [], 'relationship_types': []}
    
    async def _resolve_entities_with_graph_context(self, entity_candidates: Dict, 
                                                 similarity_matrices: Dict,
                                                 graph_contexts: Dict) -> List[Dict]:
        """Resolve entity links using both similarity and graph context"""
        
        logger.info("Resolving entities with graph context")
        
        # Create entity resolver
        resolver = EntityResolver(
            similarity_matrices=similarity_matrices,
            graph_contexts=graph_contexts,
            similarity_threshold=self.similarity_threshold,
            modality_weights=self.modality_weights
        )
        
        # Resolve entities
        linked_entities = await resolver.resolve_entities()
        
        # Enrich with original entity data
        enriched_entities = []
        for cluster in linked_entities:
            enriched_cluster = await self._enrich_linked_cluster(cluster, entity_candidates)
            enriched_entities.append(enriched_cluster)
        
        return enriched_entities
    
    async def _enrich_linked_cluster(self, cluster: Dict, entity_candidates: Dict) -> Dict:
        """Enrich linked entity cluster with original entity data"""
        
        enriched_entities = {}
        
        for modality, entity_indices in cluster['entities'].items():
            enriched_entities[modality] = []
            
            for idx in entity_indices:
                if idx < len(entity_candidates.get(modality, [])):
                    original_entity = entity_candidates[modality][idx].copy()
                    original_entity['cluster_id'] = cluster['cluster_id']
                    enriched_entities[modality].append(original_entity)
        
        return {
            'cluster_id': cluster['cluster_id'],
            'entities': enriched_entities,
            'size': cluster['size'],
            'modalities': cluster['modalities'],
            'cross_modal_count': cluster['cross_modal_count']
        }
    
    async def _build_cross_modal_graph(self, linked_entities: List[Dict]) -> Dict[str, Any]:
        """Build cross-modal entity graph"""
        
        nodes = []
        edges = []
        
        for cluster in linked_entities:
            cluster_id = cluster['cluster_id']
            
            # Create cluster node
            cluster_node = {
                'id': f"cluster_{cluster_id}",
                'type': 'entity_cluster',
                'size': cluster['size'],
                'modalities': cluster['modalities']
            }
            nodes.append(cluster_node)
            
            # Create edges between entities in the cluster
            all_entities = []
            for modality, entities in cluster['entities'].items():
                for i, entity in enumerate(entities):
                    entity_node = {
                        'id': f"{modality}_{cluster_id}_{i}",
                        'type': 'entity',
                        'modality': modality,
                        'cluster_id': cluster_id,
                        'data': entity
                    }
                    nodes.append(entity_node)
                    all_entities.append(entity_node['id'])
                    
                    # Edge from entity to cluster
                    edges.append({
                        'source': entity_node['id'],
                        'target': cluster_node['id'],
                        'type': 'belongs_to'
                    })
            
            # Edges between entities in the same cluster
            for i, entity1_id in enumerate(all_entities):
                for entity2_id in all_entities[i+1:]:
                    edges.append({
                        'source': entity1_id,
                        'target': entity2_id,
                        'type': 'linked_entity'
                    })
        
        return {
            'nodes': nodes,
            'edges': edges,
            'total_clusters': len(linked_entities),
            'total_nodes': len(nodes),
            'total_edges': len(edges)
        }
    
    async def _calculate_linking_metrics(self, entity_candidates: Dict, 
                                       linked_entities: List[Dict]) -> Dict[str, Any]:
        """Calculate linking performance metrics"""
        
        total_entities = sum(len(entities) for entities in entity_candidates.values())
        linked_entity_count = sum(cluster['size'] for cluster in linked_entities)
        
        modality_coverage = {}
        for modality in entity_candidates.keys():
            entities_in_clusters = sum(
                len(cluster['entities'].get(modality, []))
                for cluster in linked_entities
            )
            total_in_modality = len(entity_candidates[modality])
            coverage = entities_in_clusters / total_in_modality if total_in_modality > 0 else 0
            modality_coverage[modality] = coverage
        
        return {
            'total_entities': total_entities,
            'linked_entities': linked_entity_count,
            'linking_rate': linked_entity_count / total_entities if total_entities > 0 else 0,
            'total_clusters': len(linked_entities),
            'avg_cluster_size': np.mean([cluster['size'] for cluster in linked_entities]) if linked_entities else 0,
            'modality_coverage': modality_coverage,
            'cross_modal_clusters': sum(1 for cluster in linked_entities if cluster['cross_modal_count'] > 1)
        }
    
    async def _store_cross_modal_links(self, tx_id: str, linked_entities: List[Dict], 
                                     cross_modal_graph: Dict[str, Any]) -> None:
        """Store cross-modal linking results with provenance"""
        
        await self.dtm.add_operation(tx_id, 'write', 'neo4j', 'cross_modal_links', {
            'linked_entities': linked_entities,
            'cross_modal_graph': cross_modal_graph,
            'operation_type': 'cross_modal_linking_storage',
            'timestamp': datetime.now().isoformat()
        })
        
        logger.info(f"Cross-modal linking results prepared for storage - {len(linked_entities)} clusters")


# Mock service for testing compatibility
class MockEmbeddingService:
    """Mock embedding service for testing purposes"""
    
    def __init__(self):
        self.dimension = 384
        
    async def embed_text(self, text: str) -> List[float]:
        """Generate mock embedding for text"""
        # Simple hash-based mock embedding for consistency
        hash_val = hash(text)
        return [(hash_val >> i) % 100 / 100.0 for i in range(self.dimension)]
    
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate mock embeddings for batch of texts"""
        return [await self.embed_text(text) for text in texts]


