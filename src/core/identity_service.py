"""T107: Identity Service - Minimal Implementation

Three-level identity management: Surface Form → Mention → Entity
Handles entity linking, deduplication, and canonical name assignment.

This is a MINIMAL implementation focusing on:
- Basic mention creation
- Simple entity linking by name similarity
- Deduplication using exact string matching
- Canonical name assignment (first occurrence)

Deferred features:
- Complex similarity algorithms
- Advanced merging strategies  
- Full entity history tracking
"""

from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime
import uuid
import re
from pathlib import Path


@dataclass
class Mention:
    """A surface form occurrence in text."""
    id: str
    surface_form: str  # Exact text as it appears
    normalized_form: str  # Cleaned/normalized version
    start_pos: int
    end_pos: int
    source_ref: str  # Reference to source document/chunk
    confidence: float = 0.8
    created_at: datetime = field(default_factory=datetime.now)


@dataclass  
class Entity:
    """A canonical entity with one or more mentions."""
    id: str
    canonical_name: str  # Primary identifier
    entity_type: Optional[str] = None
    mentions: List[str] = field(default_factory=list)  # Mention IDs
    confidence: float = 0.8
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class IdentityService:
    """T107: Identity Service - Three-level identity management."""
    
    def __init__(self):
        self.mentions: Dict[str, Mention] = {}
        self.entities: Dict[str, Entity] = {} 
        self.surface_to_mentions: Dict[str, Set[str]] = {}  # normalized_form -> mention_ids
        self.mention_to_entity: Dict[str, str] = {}  # mention_id -> entity_id
        
    def create_mention(
        self,
        surface_form: str,
        start_pos: int,
        end_pos: int,
        source_ref: str,
        entity_type: Optional[str] = None,
        confidence: float = 0.8
    ) -> Dict[str, Any]:
        """Create a new mention and optionally link to entity.
        
        Args:
            surface_form: Exact text as it appears
            start_pos: Start character position
            end_pos: End character position  
            source_ref: Reference to source (storage://type/id)
            entity_type: Optional entity type hint
            confidence: Confidence score (0.0-1.0)
            
        Returns:
            Dict with mention_id and entity_id (if linked)
        """
        try:
            # Input validation
            if not surface_form or not surface_form.strip():
                return {
                    "status": "error",
                    "error": "surface_form cannot be empty",
                    "confidence": 0.0
                }
                
            if start_pos < 0 or end_pos <= start_pos:
                return {
                    "status": "error", 
                    "error": "Invalid position range",
                    "confidence": 0.0
                }
                
            if not (0.0 <= confidence <= 1.0):
                return {
                    "status": "error",
                    "error": "Confidence must be between 0.0 and 1.0", 
                    "confidence": 0.0
                }
            
            # Create mention
            mention_id = f"mention_{uuid.uuid4().hex[:8]}"
            normalized_form = self._normalize_surface_form(surface_form)
            
            mention = Mention(
                id=mention_id,
                surface_form=surface_form,
                normalized_form=normalized_form,
                start_pos=start_pos,
                end_pos=end_pos,
                source_ref=source_ref,
                confidence=confidence
            )
            
            # Store mention
            self.mentions[mention_id] = mention
            
            # Update surface form index
            if normalized_form not in self.surface_to_mentions:
                self.surface_to_mentions[normalized_form] = set()
            self.surface_to_mentions[normalized_form].add(mention_id)
            
            # Try to link to existing entity or create new one
            entity_id = self._link_or_create_entity(
                mention_id, normalized_form, entity_type, confidence
            )
            
            return {
                "status": "success",
                "mention_id": mention_id,
                "entity_id": entity_id,
                "normalized_form": normalized_form,
                "confidence": confidence
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to create mention: {str(e)}",
                "confidence": 0.0
            }
    
    def _normalize_surface_form(self, surface_form: str) -> str:
        """Normalize surface form for entity matching."""
        # Simple normalization: lowercase, strip, collapse whitespace
        normalized = re.sub(r'\s+', ' ', surface_form.strip().lower())
        return normalized
    
    def _link_or_create_entity(
        self, 
        mention_id: str, 
        normalized_form: str,
        entity_type: Optional[str],
        confidence: float
    ) -> str:
        """Link mention to existing entity or create new one."""
        
        # Look for existing entity with same normalized form
        existing_entity_id = self._find_matching_entity(normalized_form, entity_type)
        
        if existing_entity_id:
            # Link to existing entity
            self.entities[existing_entity_id].mentions.append(mention_id)
            self.mention_to_entity[mention_id] = existing_entity_id
            
            # Update entity confidence (simple average)
            entity = self.entities[existing_entity_id]
            mention_count = len(entity.mentions)
            entity.confidence = (entity.confidence * (mention_count - 1) + confidence) / mention_count
            
            return existing_entity_id
        else:
            # Create new entity
            entity_id = f"entity_{uuid.uuid4().hex[:8]}"
            entity = Entity(
                id=entity_id,
                canonical_name=normalized_form,  # Use normalized form as canonical name
                entity_type=entity_type,
                mentions=[mention_id],
                confidence=confidence
            )
            
            self.entities[entity_id] = entity
            self.mention_to_entity[mention_id] = entity_id
            
            return entity_id
    
    def _find_matching_entity(self, normalized_form: str, entity_type: Optional[str]) -> Optional[str]:
        """Find existing entity that matches the normalized form."""
        # Simple exact match for now
        for entity_id, entity in self.entities.items():
            if entity.canonical_name == normalized_form:
                # If type is specified, ensure it matches
                if entity_type and entity.entity_type and entity.entity_type != entity_type:
                    continue
                return entity_id
        return None
    
    def get_entity_by_mention(self, mention_id: str) -> Optional[Dict[str, Any]]:
        """Get entity associated with a mention."""
        try:
            if mention_id not in self.mention_to_entity:
                return None
                
            entity_id = self.mention_to_entity[mention_id]
            entity = self.entities.get(entity_id)
            
            if not entity:
                return None
                
            return {
                "entity_id": entity.id,
                "canonical_name": entity.canonical_name,
                "entity_type": entity.entity_type,
                "mention_count": len(entity.mentions),
                "confidence": entity.confidence,
                "created_at": entity.created_at.isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to get entity: {str(e)}"
            }
    
    def get_mentions_for_entity(self, entity_id: str) -> List[Dict[str, Any]]:
        """Get all mentions for an entity."""
        try:
            entity = self.entities.get(entity_id)
            if not entity:
                return []
                
            mentions = []
            for mention_id in entity.mentions:
                mention = self.mentions.get(mention_id)
                if mention:
                    mentions.append({
                        "mention_id": mention.id,
                        "surface_form": mention.surface_form,
                        "normalized_form": mention.normalized_form,
                        "start_pos": mention.start_pos,
                        "end_pos": mention.end_pos,
                        "source_ref": mention.source_ref,
                        "confidence": mention.confidence
                    })
            
            return mentions
            
        except Exception as e:
            return []
    
    def merge_entities(self, entity_id1: str, entity_id2: str) -> Dict[str, Any]:
        """Merge two entities (keeping the first one)."""
        try:
            if entity_id1 not in self.entities or entity_id2 not in self.entities:
                return {
                    "status": "error",
                    "error": "One or both entities not found"
                }
            
            entity1 = self.entities[entity_id1]
            entity2 = self.entities[entity_id2]
            
            # Merge mentions
            entity1.mentions.extend(entity2.mentions)
            
            # Update mention-to-entity mapping
            for mention_id in entity2.mentions:
                self.mention_to_entity[mention_id] = entity_id1
            
            # Update confidence (weighted average)
            total_mentions = len(entity1.mentions)
            entity1_mentions = total_mentions - len(entity2.mentions)
            entity2_mentions = len(entity2.mentions)
            
            entity1.confidence = (
                (entity1.confidence * entity1_mentions + entity2.confidence * entity2_mentions) 
                / total_mentions
            )
            
            # Remove merged entity
            del self.entities[entity_id2]
            
            return {
                "status": "success",
                "merged_entity_id": entity_id1,
                "removed_entity_id": entity_id2,
                "total_mentions": total_mentions,
                "confidence": entity1.confidence
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to merge entities: {str(e)}"
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get identity service statistics."""
        return {
            "total_mentions": len(self.mentions),
            "total_entities": len(self.entities),
            "unique_surface_forms": len(self.surface_to_mentions),
            "avg_mentions_per_entity": (
                len(self.mentions) / len(self.entities) if self.entities else 0
            )
        }