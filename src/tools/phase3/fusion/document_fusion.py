"""
Document Fusion Core Logic

Extracted from t301_multi_document_fusion.py (lines ~765-1800)
Core document fusion algorithms focusing on entity similarity and clustering.
"""

import logging
from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)


class DocumentFusion:
    """Core document fusion logic for multi-document knowledge consolidation."""
    
    def __init__(self, 
                 identity_service=None, 
                 quality_service=None,
                 similarity_threshold: float = 0.8,
                 confidence_threshold: float = 0.7):
        """Initialize document fusion with configurable thresholds."""
        self.identity_service = identity_service
        self.quality_service = quality_service
        self.similarity_threshold = similarity_threshold
        self.confidence_threshold = confidence_threshold
        self.logger = logging.getLogger(f"{__name__}.DocumentFusion")
        
    def fuse_documents(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Main document fusion method.
        
        Args:
            documents: List of processed documents with entities and relationships
            
        Returns:
            Dict containing fused entities, relationships, and fusion metadata
        """
        self.logger.info(f"Starting fusion of {len(documents)} documents")
        
        try:
            # Extract all entities and relationships from documents
            all_entities = []
            all_relationships = []
            
            for doc in documents:
                all_entities.extend(doc.get('entities', []))
                all_relationships.extend(doc.get('relationships', []))
            
            # Fuse entities using similarity-based clustering
            fused_entities = self._fuse_entities(all_entities)
            
            # Fuse relationships based on entity mappings
            fused_relationships = self._fuse_relationships(all_relationships, fused_entities)
            
            # Calculate fusion statistics
            fusion_stats = self._calculate_fusion_stats(
                all_entities, fused_entities,
                all_relationships, fused_relationships
            )
            
            result = {
                'fused_entities': fused_entities,
                'fused_relationships': fused_relationships,
                'fusion_statistics': fusion_stats,
                'documents_processed': len(documents),
                'fusion_timestamp': datetime.now().isoformat()
            }
            
            self.logger.info(f"Fusion completed: {fusion_stats}")
            return result
            
        except Exception as e:
            self.logger.error(f"Document fusion failed: {e}", exc_info=True)
            return {
                'error': str(e),
                'fused_entities': [],
                'fused_relationships': [],
                'fusion_statistics': {},
                'documents_processed': len(documents)
            }
    
    def _fuse_entities(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Fuse entities using similarity-based clustering."""
        if not entities:
            return []
        
        # Group entities by type for more efficient processing
        entities_by_type = defaultdict(list)
        for entity in entities:
            entity_type = entity.get('type', 'UNKNOWN')
            entities_by_type[entity_type].append(entity)
        
        fused_entities = []
        
        # Process each entity type separately
        for entity_type, type_entities in entities_by_type.items():
            fused_type_entities = self._fuse_entities_of_type(type_entities)
            fused_entities.extend(fused_type_entities)
        
        return fused_entities
    
    def _fuse_entities_of_type(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Fuse entities of the same type using similarity clustering."""
        if len(entities) <= 1:
            return entities
            
        # Build similarity matrix
        similarity_matrix = self._build_similarity_matrix(entities)
        
        # Find clusters using threshold-based clustering
        clusters = self._find_entity_clusters(entities, similarity_matrix)
        
        # Merge entities within each cluster
        fused_entities = []
        for cluster in clusters:
            if len(cluster) == 1:
                fused_entities.append(cluster[0])
            else:
                merged_entity = self._merge_entity_cluster(cluster)
                fused_entities.append(merged_entity)
        
        return fused_entities
    
    def _build_similarity_matrix(self, entities: List[Dict[str, Any]]) -> List[List[float]]:
        """Build entity similarity matrix."""
        n = len(entities)
        matrix = [[0.0 for _ in range(n)] for _ in range(n)]
        
        for i in range(n):
            for j in range(i + 1, n):
                similarity = self._calculate_entity_similarity(entities[i], entities[j])
                matrix[i][j] = similarity
                matrix[j][i] = similarity
        
        return matrix
    
    def _calculate_entity_similarity(self, entity1: Dict[str, Any], entity2: Dict[str, Any]) -> float:
        """Calculate similarity between two entities."""
        name1 = entity1.get('name', '').lower().strip()
        name2 = entity2.get('name', '').lower().strip()
        
        if not name1 or not name2:
            return 0.0
        
        # Exact match
        if name1 == name2:
            return 1.0
        
        # Substring match
        if name1 in name2 or name2 in name1:
            shorter = min(len(name1), len(name2))
            longer = max(len(name1), len(name2))
            return shorter / longer * 0.9  # Slight penalty for substring match
        
        # Word overlap similarity
        words1 = set(name1.split())
        words2 = set(name2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    def _find_entity_clusters(self, entities: List[Dict[str, Any]], 
                            similarity_matrix: List[List[float]]) -> List[List[Dict[str, Any]]]:
        """Find entity clusters using threshold-based clustering."""
        n = len(entities)
        visited = [False] * n
        clusters = []
        
        for i in range(n):
            if visited[i]:
                continue
                
            # Start new cluster
            cluster = [entities[i]]
            visited[i] = True
            
            # Find similar entities
            for j in range(i + 1, n):
                if not visited[j] and similarity_matrix[i][j] >= self.similarity_threshold:
                    cluster.append(entities[j])
                    visited[j] = True
            
            clusters.append(cluster)
        
        return clusters
    
    def _merge_entity_cluster(self, cluster: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Merge entities within a cluster into a single representative entity."""
        if len(cluster) == 1:
            return cluster[0]
        
        # Find the entity with highest confidence as base
        base_entity = max(cluster, key=lambda e: e.get('confidence', 0.0))
        
        # Merge information from all entities
        merged = {
            'name': base_entity.get('name', ''),
            'type': base_entity.get('type', ''),
            'confidence': self._calculate_merged_confidence(cluster),
            'sources': [],
            'mentions': [],
            'properties': {}
        }
        
        # Collect sources, mentions, and properties
        for entity in cluster:
            if 'source' in entity:
                merged['sources'].append(entity['source'])
            if 'mentions' in entity:
                merged['mentions'].extend(entity['mentions'])
            if 'properties' in entity:
                merged['properties'].update(entity['properties'])
        
        # Remove duplicates from sources
        merged['sources'] = list(set(merged['sources']))
        
        return merged
    
    def _calculate_merged_confidence(self, cluster: List[Dict[str, Any]]) -> float:
        """Calculate confidence for merged entity cluster."""
        confidences = [e.get('confidence', 0.0) for e in cluster]
        
        if not confidences:
            return 0.0
        
        # Use weighted average with bias toward higher confidence
        weights = [c ** 2 for c in confidences]  # Square for emphasis
        total_weight = sum(weights)
        
        if total_weight == 0:
            return sum(confidences) / len(confidences)
        
        weighted_sum = sum(c * w for c, w in zip(confidences, weights))
        return min(weighted_sum / total_weight, 1.0)
    
    def _fuse_relationships(self, relationships: List[Dict[str, Any]], 
                          fused_entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Fuse relationships based on entity mappings from fusion."""
        if not relationships:
            return []
        
        # Create entity name to fused entity mapping
        entity_mapping = self._create_entity_mapping(fused_entities)
        
        # Group relationships by (source, target, type) after mapping
        relationship_groups = defaultdict(list)
        
        for rel in relationships:
            source = rel.get('source', '')
            target = rel.get('target', '')
            rel_type = rel.get('type', '')
            
            # Map to fused entities
            mapped_source = entity_mapping.get(source.lower(), source)
            mapped_target = entity_mapping.get(target.lower(), target)
            
            key = (mapped_source, mapped_target, rel_type)
            relationship_groups[key].append(rel)
        
        # Merge relationships in each group
        fused_relationships = []
        for (source, target, rel_type), group in relationship_groups.items():
            if len(group) == 1:
                fused_relationships.append(group[0])
            else:
                merged_rel = self._merge_relationship_group(group, source, target, rel_type)
                fused_relationships.append(merged_rel)
        
        return fused_relationships
    
    def _create_entity_mapping(self, fused_entities: List[Dict[str, Any]]) -> Dict[str, str]:
        """Create mapping from original entity names to fused entity names."""
        mapping = {}
        
        for entity in fused_entities:
            entity_name = entity.get('name', '')
            
            # Map the main name
            mapping[entity_name.lower()] = entity_name
            
            # Map alternative mentions/names if present
            mentions = entity.get('mentions', [])
            for mention in mentions:
                if isinstance(mention, str):
                    mapping[mention.lower()] = entity_name
                elif isinstance(mention, dict) and 'name' in mention:
                    mapping[mention['name'].lower()] = entity_name
        
        return mapping
    
    def _merge_relationship_group(self, group: List[Dict[str, Any]], 
                                source: str, target: str, rel_type: str) -> Dict[str, Any]:
        """Merge a group of similar relationships."""
        # Find relationship with highest confidence as base
        base_rel = max(group, key=lambda r: r.get('confidence', 0.0))
        
        merged = {
            'source': source,
            'target': target,
            'type': rel_type,
            'confidence': self._calculate_merged_confidence(group),
            'evidence': [],
            'sources': []
        }
        
        # Collect evidence and sources
        for rel in group:
            if 'evidence' in rel:
                evidence = rel['evidence']
                if isinstance(evidence, str):
                    merged['evidence'].append(evidence)
                elif isinstance(evidence, list):
                    merged['evidence'].extend(evidence)
            
            if 'source' in rel:
                merged['sources'].append(rel['source'])
        
        # Remove duplicates
        merged['evidence'] = list(set(merged['evidence']))
        merged['sources'] = list(set(merged['sources']))
        
        return merged
    
    def _calculate_fusion_stats(self, original_entities: List[Dict[str, Any]], 
                              fused_entities: List[Dict[str, Any]],
                              original_relationships: List[Dict[str, Any]], 
                              fused_relationships: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate fusion statistics."""
        return {
            'entities_before_fusion': len(original_entities),
            'entities_after_fusion': len(fused_entities),
            'entities_merged': len(original_entities) - len(fused_entities),
            'entity_reduction_ratio': 1 - (len(fused_entities) / len(original_entities)) if original_entities else 0,
            'relationships_before_fusion': len(original_relationships),
            'relationships_after_fusion': len(fused_relationships),
            'relationships_merged': len(original_relationships) - len(fused_relationships),
            'relationship_reduction_ratio': 1 - (len(fused_relationships) / len(original_relationships)) if original_relationships else 0
        }