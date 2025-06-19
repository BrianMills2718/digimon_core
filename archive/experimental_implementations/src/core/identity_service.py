"""T107: Identity Service - Three-level identity management."""

import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict

from ..models import Entity, Mention, SurfaceForm, Reference
from ..utils.database import DatabaseManager


logger = logging.getLogger(__name__)


@dataclass
class IdentityResolution:
    """Result of identity resolution."""
    
    entity_id: str
    confidence: float
    evidence: List[str]
    alternate_entities: List[Tuple[str, float]]  # (entity_id, confidence)


class IdentityService:
    """
    T107: Identity Service
    
    Manages three-level identity system:
    1. Surface Form - Text as it appears
    2. Mention - Specific occurrence with context
    3. Entity - Resolved canonical entity
    """
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self._surface_cache: Dict[str, List[str]] = defaultdict(list)
        self._entity_cache: Dict[str, Entity] = {}
    
    def create_surface_form(
        self,
        text: str,
        context: str,
        chunk_id: str,
        start_offset: int,
        end_offset: int,
        confidence: float = 1.0
    ) -> SurfaceForm:
        """Create a new surface form."""
        surface_form = SurfaceForm(
            text=text,
            context=context,
            chunk_id=chunk_id,
            start_offset=start_offset,
            end_offset=end_offset,
            confidence=confidence
        )
        
        # Store in SQLite
        self.db.sqlite.save_surface_form(surface_form)
        
        # Update cache
        normalized_text = self._normalize_text(text)
        self._surface_cache[normalized_text].append(surface_form.id)
        
        logger.debug(f"Created surface form: {surface_form.id} for text: {text}")
        return surface_form
    
    def create_mention(
        self,
        surface_form_id: str,
        mention_type: str,
        attributes: Dict[str, Any],
        confidence: float = 1.0
    ) -> Mention:
        """Create a new mention from a surface form."""
        mention = Mention(
            surface_form_id=surface_form_id,
            mention_type=mention_type,
            attributes=attributes,
            confidence=confidence
        )
        
        # Store in SQLite
        self.db.sqlite.save_mention(mention)
        
        logger.debug(f"Created mention: {mention.id} of type: {mention_type}")
        return mention
    
    def resolve_entity(
        self,
        mention_id: str,
        resolution_method: str = "exact_match"
    ) -> IdentityResolution:
        """Resolve a mention to an entity."""
        # Get mention and surface form
        mention = self.db.sqlite.get_mention(mention_id)
        if not mention:
            raise ValueError(f"Mention not found: {mention_id}")
        
        surface_form = self.db.sqlite.get_surface_form(mention.surface_form_id)
        if not surface_form:
            raise ValueError(f"Surface form not found: {mention.surface_form_id}")
        
        # Try different resolution methods
        if resolution_method == "exact_match":
            resolution = self._resolve_exact_match(surface_form, mention)
        elif resolution_method == "fuzzy_match":
            resolution = self._resolve_fuzzy_match(surface_form, mention)
        elif resolution_method == "contextual":
            resolution = self._resolve_contextual(surface_form, mention)
        else:
            raise ValueError(f"Unknown resolution method: {resolution_method}")
        
        # Update mention with resolved entity
        if resolution and resolution.confidence > 0.5:
            mention.entity_id = resolution.entity_id
            mention.confidence *= resolution.confidence
            mention.evidence.extend(resolution.evidence)
            self.db.sqlite.update_mention(mention)
        
        return resolution
    
    def merge_entities(
        self,
        entity_ids: List[str],
        canonical_id: Optional[str] = None
    ) -> Entity:
        """Merge multiple entities into one canonical entity."""
        if len(entity_ids) < 2:
            raise ValueError("Need at least 2 entities to merge")
        
        # Load all entities
        entities = []
        for entity_id in entity_ids:
            entity = self.db.neo4j.get_entity(entity_id)
            if entity:
                entities.append(entity)
        
        if not entities:
            raise ValueError("No valid entities found")
        
        # Choose canonical entity (highest confidence or specified)
        if canonical_id:
            canonical = next((e for e in entities if e.id == canonical_id), None)
            if not canonical:
                raise ValueError(f"Canonical entity not found: {canonical_id}")
        else:
            canonical = max(entities, key=lambda e: e.confidence)
        
        # Merge data
        all_surface_forms = set()
        all_mention_refs = []
        merged_attributes = {}
        min_confidence = canonical.confidence
        
        for entity in entities:
            if entity.id == canonical.id:
                continue
            
            # Merge surface forms
            all_surface_forms.update(entity.surface_forms)
            
            # Merge mentions
            all_mention_refs.extend(entity.mention_refs)
            
            # Merge attributes (canonical takes precedence)
            for key, value in entity.attributes.items():
                if key not in merged_attributes:
                    merged_attributes[key] = value
            
            # Track minimum confidence
            min_confidence = min(min_confidence, entity.confidence)
            
            # Update mentions to point to canonical
            for mention_ref in entity.mention_refs:
                mention_id = Reference.from_string(mention_ref).id
                mention = self.db.sqlite.get_mention(mention_id)
                if mention:
                    mention.entity_id = canonical.id
                    self.db.sqlite.update_mention(mention)
            
            # Delete merged entity
            self.db.neo4j.delete_entity(entity.id)
        
        # Update canonical entity
        canonical.surface_forms = list(set(canonical.surface_forms) | all_surface_forms)
        canonical.mention_refs.extend(all_mention_refs)
        canonical.attributes.update(merged_attributes)
        canonical.confidence = min_confidence * 0.95  # Small confidence penalty for merge
        canonical.add_warning(f"Merged from {len(entities)} entities")
        
        self.db.neo4j.update_entity(canonical)
        
        logger.info(f"Merged {len(entities)} entities into {canonical.id}")
        return canonical
    
    def get_entity_by_surface_form(self, text: str) -> List[Entity]:
        """Get all entities that have a given surface form."""
        normalized = self._normalize_text(text)
        
        # Find all mentions with this surface form
        surface_form_ids = self._surface_cache.get(normalized, [])
        entity_ids = set()
        
        for sf_id in surface_form_ids:
            mentions = self.db.sqlite.get_mentions_by_surface_form(sf_id)
            for mention in mentions:
                if mention.entity_id:
                    entity_ids.add(mention.entity_id)
        
        # Load entities
        entities = []
        for entity_id in entity_ids:
            entity = self.db.neo4j.get_entity(entity_id)
            if entity:
                entities.append(entity)
        
        return sorted(entities, key=lambda e: e.confidence, reverse=True)
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for matching."""
        return text.lower().strip()
    
    def _resolve_exact_match(
        self,
        surface_form: SurfaceForm,
        mention: Mention
    ) -> Optional[IdentityResolution]:
        """Resolve by exact text match."""
        entities = self.get_entity_by_surface_form(surface_form.text)
        
        if not entities:
            return None
        
        # Return highest confidence match
        best_entity = entities[0]
        return IdentityResolution(
            entity_id=best_entity.id,
            confidence=0.9,  # High confidence for exact match
            evidence=[f"Exact match: {surface_form.text}"],
            alternate_entities=[(e.id, 0.9) for e in entities[1:3]]
        )
    
    def _resolve_fuzzy_match(
        self,
        surface_form: SurfaceForm,
        mention: Mention
    ) -> Optional[IdentityResolution]:
        """Resolve by fuzzy text matching."""
        # TODO: Implement fuzzy matching logic
        # For now, fallback to exact match
        return self._resolve_exact_match(surface_form, mention)
    
    def _resolve_contextual(
        self,
        surface_form: SurfaceForm,
        mention: Mention
    ) -> Optional[IdentityResolution]:
        """Resolve using context and attributes."""
        # TODO: Implement contextual resolution
        # For now, fallback to exact match
        return self._resolve_exact_match(surface_form, mention)
    
    def create_or_link_entity(
        self,
        surface_form: str,
        entity_type: str,
        attributes: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a new entity or link to existing one.
        
        Returns:
            Dictionary with:
            - entity: The entity object
            - is_new: Whether a new entity was created
            - confidence: Resolution confidence
        """
        # Check if entity already exists with this surface form
        existing_entities = self.get_entity_by_surface_form(surface_form)
        
        if existing_entities:
            # Return the best match
            entity = existing_entities[0]
            return {
                "entity": entity,
                "is_new": False,
                "confidence": 0.9  # High confidence for existing entity
            }
        
        # Create new entity
        entity = Entity(
            name=surface_form,
            entity_type=entity_type,
            canonical_name=surface_form,
            attributes=attributes or {}
        )
        
        # Save to Neo4j
        self.db.neo4j.save_entity(entity)
        
        # Cache it
        self._entity_cache[entity.id] = entity
        self._surface_cache[self._normalize_text(surface_form)].append(entity.id)
        
        return {
            "entity": entity,
            "is_new": True,
            "confidence": 1.0  # Full confidence for new entity
        }