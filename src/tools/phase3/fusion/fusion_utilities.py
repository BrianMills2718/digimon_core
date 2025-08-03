"""
Fusion Utilities

Extracted from t301_multi_document_fusion.py (utility functions and helper methods)
Common utilities used across the fusion pipeline.
"""

import logging
import time
import hashlib
from typing import List, Dict, Any, Optional, Set
from datetime import datetime
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)


class FusionUtilities:
    """Utility functions for document fusion operations."""
    
    def __init__(self):
        """Initialize fusion utilities."""
        self.logger = logging.getLogger(f"{__name__}.FusionUtilities")
    
    def generate_fusion_id(self, entities: List[Dict[str, Any]]) -> str:
        """Generate unique ID for fusion operation."""
        # Create deterministic hash from entity names and types
        entity_signatures = []
        for entity in entities:
            signature = f"{entity.get('name', '')}-{entity.get('type', '')}"
            entity_signatures.append(signature)
        
        entity_signatures.sort()  # Ensure deterministic ordering
        combined = "|".join(entity_signatures)
        
        fusion_hash = hashlib.md5(combined.encode()).hexdigest()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        return f"fusion_{timestamp}_{fusion_hash[:8]}"
    
    def normalize_entity_name(self, name: str) -> str:
        """Normalize entity name for comparison."""
        if not name:
            return ""
        
        # Basic normalization
        normalized = name.strip().lower()
        
        # Remove common prefixes/suffixes
        prefixes = ["dr.", "prof.", "mr.", "mrs.", "ms."]
        suffixes = ["inc.", "corp.", "ltd.", "llc"]
        
        for prefix in prefixes:
            if normalized.startswith(prefix):
                normalized = normalized[len(prefix):].strip()
                break
        
        for suffix in suffixes:
            if normalized.endswith(suffix):
                normalized = normalized[:-len(suffix)].strip()
                break
        
        return normalized
    
    def calculate_jaccard_similarity(self, set1: Set[str], set2: Set[str]) -> float:
        """Calculate Jaccard similarity between two sets."""
        if not set1 and not set2:
            return 1.0
        
        if not set1 or not set2:
            return 0.0
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0
    
    def extract_entity_features(self, entity: Dict[str, Any]) -> Dict[str, Any]:
        """Extract features from entity for similarity comparison."""
        features = {
            'normalized_name': self.normalize_entity_name(entity.get('name', '')),
            'entity_type': entity.get('type', '').upper(),
            'confidence': entity.get('confidence', 0.0),
            'source_count': len(entity.get('sources', [])),
            'mention_count': len(entity.get('mentions', [])),
            'property_count': len(entity.get('properties', {}))
        }
        
        # Extract word features
        name_words = set(features['normalized_name'].split())
        features['word_count'] = len(name_words)
        features['name_words'] = name_words
        
        # Extract contextual features
        properties = entity.get('properties', {})
        features['has_dates'] = any(
            key in properties for key in ['founded', 'born', 'created', 'established']
        )
        features['has_location'] = any(
            key in properties for key in ['location', 'address', 'city', 'country']
        )
        
        return features
    
    def validate_entity_structure(self, entity: Dict[str, Any]) -> bool:
        """Validate entity has required structure."""
        required_fields = ['name', 'type']
        
        for field in required_fields:
            if field not in entity or not entity[field]:
                self.logger.warning(f"Entity missing required field: {field}")
                return False
        
        # Validate confidence if present
        if 'confidence' in entity:
            confidence = entity['confidence']
            if not isinstance(confidence, (int, float)) or not (0.0 <= confidence <= 1.0):
                self.logger.warning(f"Invalid confidence value: {confidence}")
                return False
        
        return True
    
    def validate_relationship_structure(self, relationship: Dict[str, Any]) -> bool:
        """Validate relationship has required structure."""
        required_fields = ['source', 'target', 'type']
        
        for field in required_fields:
            if field not in relationship or not relationship[field]:
                self.logger.warning(f"Relationship missing required field: {field}")
                return False
        
        # Check for self-references
        if relationship['source'] == relationship['target']:
            self.logger.warning("Relationship contains self-reference")
            return False
        
        return True
    
    def group_entities_by_type(self, entities: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group entities by their type."""
        groups = defaultdict(list)
        
        for entity in entities:
            entity_type = entity.get('type', 'UNKNOWN').upper()
            groups[entity_type].append(entity)
        
        return dict(groups)
    
    def calculate_fusion_quality_score(self, 
                                     original_count: int, 
                                     fused_count: int,
                                     conflicts_resolved: int) -> float:
        """Calculate overall fusion quality score."""
        if original_count == 0:
            return 1.0 if fused_count == 0 else 0.0
        
        # Reduction ratio (higher reduction = better fusion)
        reduction_ratio = 1 - (fused_count / original_count)
        
        # Conflict resolution ratio
        max_possible_conflicts = original_count * (original_count - 1) // 2
        conflict_resolution_ratio = conflicts_resolved / max(max_possible_conflicts, 1)
        
        # Weighted combination
        quality_score = (0.7 * reduction_ratio) + (0.3 * min(conflict_resolution_ratio, 1.0))
        
        return max(0.0, min(1.0, quality_score))
    
    def format_fusion_summary(self, stats: Dict[str, Any]) -> str:
        """Format fusion statistics into readable summary."""
        summary_parts = [
            f"📊 Fusion Summary:",
            f"  • Entities: {stats.get('entities_before_fusion', 0)} → {stats.get('entities_after_fusion', 0)}",
            f"  • Relationships: {stats.get('relationships_before_fusion', 0)} → {stats.get('relationships_after_fusion', 0)}",
            f"  • Conflicts resolved: {stats.get('conflicts_resolved', 0)}",
            f"  • Quality score: {stats.get('quality_score', 0.0):.3f}"
        ]
        
        if 'fusion_time_seconds' in stats:
            summary_parts.append(f"  • Processing time: {stats['fusion_time_seconds']:.2f}s")
        
        return "\n".join(summary_parts)
    
    def create_fusion_metadata(self, 
                             fusion_id: str,
                             strategy: str,
                             parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Create metadata for fusion operation."""
        return {
            'fusion_id': fusion_id,
            'fusion_strategy': strategy,
            'fusion_timestamp': datetime.now().isoformat(),
            'fusion_parameters': parameters.copy(),
            'tool_version': '1.0.0',
            'created_by': 'DocumentFusion'
        }
    
    def merge_entity_properties(self, entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Merge properties from multiple entities."""
        merged_properties = {}
        
        for entity in entities:
            properties = entity.get('properties', {})
            for key, value in properties.items():
                if key not in merged_properties:
                    merged_properties[key] = value
                elif merged_properties[key] != value:
                    # Handle conflicts - prefer non-empty values
                    if not merged_properties[key] and value:
                        merged_properties[key] = value
                    elif isinstance(value, (list, tuple)) and isinstance(merged_properties[key], (list, tuple)):
                        # Merge lists
                        merged_list = list(merged_properties[key]) + list(value)
                        merged_properties[key] = list(set(merged_list))  # Remove duplicates
        
        return merged_properties
    
    def calculate_entity_importance_score(self, entity: Dict[str, Any]) -> float:
        """Calculate importance score for entity."""
        score = 0.0
        
        # Base confidence
        confidence = entity.get('confidence', 0.0)
        score += confidence * 0.4
        
        # Number of sources
        source_count = len(entity.get('sources', []))
        score += min(source_count / 10.0, 0.3)  # Max 0.3 for sources
        
        # Number of mentions
        mention_count = len(entity.get('mentions', []))
        score += min(mention_count / 20.0, 0.2)  # Max 0.2 for mentions
        
        # Property richness
        property_count = len(entity.get('properties', {}))
        score += min(property_count / 10.0, 0.1)  # Max 0.1 for properties
        
        return min(score, 1.0)
    
    def detect_potential_duplicates(self, entities: List[Dict[str, Any]], 
                                  similarity_threshold: float = 0.7) -> List[List[Dict[str, Any]]]:
        """Detect potential duplicate entities."""
        potential_duplicates = []
        processed = set()
        
        for i, entity1 in enumerate(entities):
            if i in processed:
                continue
            
            duplicates = [entity1]
            processed.add(i)
            
            for j, entity2 in enumerate(entities[i+1:], i+1):
                if j in processed:
                    continue
                
                # Quick type check
                if entity1.get('type') != entity2.get('type'):
                    continue
                
                # Calculate similarity
                features1 = self.extract_entity_features(entity1)
                features2 = self.extract_entity_features(entity2)
                
                name_similarity = self.calculate_jaccard_similarity(
                    features1['name_words'], 
                    features2['name_words']
                )
                
                if name_similarity >= similarity_threshold:
                    duplicates.append(entity2)
                    processed.add(j)
            
            if len(duplicates) > 1:
                potential_duplicates.append(duplicates)
        
        return potential_duplicates
    
    def get_tool_info(self) -> Dict[str, Any]:
        """Get tool information for MCP compatibility."""
        return {
            'tool_name': 'FusionUtilities',
            'description': 'Utility functions for document fusion operations',
            'version': '1.0.0',
            'capabilities': [
                'entity_normalization',
                'similarity_calculation', 
                'structure_validation',
                'duplicate_detection',
                'quality_scoring',
                'metadata_generation'
            ],
            'utility_functions': [
                'generate_fusion_id',
                'normalize_entity_name',
                'calculate_jaccard_similarity',
                'extract_entity_features',
                'validate_entity_structure',
                'validate_relationship_structure',
                'group_entities_by_type',
                'calculate_fusion_quality_score',
                'format_fusion_summary',
                'create_fusion_metadata',
                'merge_entity_properties',
                'calculate_entity_importance_score',
                'detect_potential_duplicates'
            ]
        }