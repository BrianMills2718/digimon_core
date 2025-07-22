"""Identity Service with Unified Service Protocol

This is the migrated version of IdentityService that implements the
standardized ServiceProtocol interface while maintaining backward compatibility.
"""

import time
import logging
from typing import Dict, Any, Optional, List, Set
from datetime import datetime
from dataclasses import dataclass
import uuid

from .service_protocol import (
    CoreService, ServiceType, ServiceInfo, ServiceOperation,
    ServiceStatus, ServiceHealth, ServiceMetrics
)

logger = logging.getLogger(__name__)


@dataclass
class EntityInfo:
    """Entity information structure"""
    entity_id: str
    canonical_name: str
    entity_type: str
    confidence: float
    mention_ids: List[str]
    created_at: str
    last_updated: str


@dataclass
class MentionInfo:
    """Mention information structure"""
    mention_id: str
    entity_id: str
    surface_form: str
    source_ref: str
    start_pos: int
    end_pos: int
    confidence: float
    created_at: str


class IdentityServiceUnified(CoreService):
    """T107: Identity resolution and entity management service
    
    Implements the unified ServiceProtocol interface while maintaining
    all existing functionality for entity and mention management.
    """
    
    def __init__(self):
        """Initialize identity service"""
        super().__init__(
            service_id="T107_IDENTITY_SERVICE",
            service_type=ServiceType.IDENTITY
        )
        
        # Core data structures
        self.entities: Dict[str, EntityInfo] = {}
        self.mentions: Dict[str, MentionInfo] = {}
        self.surface_to_entities: Dict[str, Set[str]] = {}
        self.entity_to_mentions: Dict[str, Set[str]] = {}
        
        # Configuration defaults
        self.config = {
            "min_confidence": 0.5,
            "merge_threshold": 0.8,
            "max_entities": 1000000,
            "max_mentions": 5000000,
            "cache_enabled": True
        }
        
        # Register health checks
        self.register_health_check("data_integrity", self._check_data_integrity)
        self.register_health_check("capacity", self._check_capacity)
        self.register_health_check("performance", self._check_performance)
    
    def get_service_info(self) -> ServiceInfo:
        """Get service metadata and capabilities"""
        return ServiceInfo(
            service_id=self.service_id,
            name="Identity Resolution Service",
            version="2.0.0",  # Version 2 indicates unified interface
            description="Manages entity identity resolution and mention tracking",
            service_type=self.service_type,
            dependencies=[],  # No external dependencies
            capabilities=[
                "entity_creation",
                "mention_creation",
                "entity_resolution",
                "mention_linking",
                "entity_merging",
                "confidence_tracking"
            ],
            configuration=self.config,
            health_endpoints=[
                "data_integrity",
                "capacity",
                "performance"
            ]
        )
    
    def initialize(self, config: Dict[str, Any]) -> ServiceOperation:
        """Initialize service with configuration"""
        start_time = time.time()
        
        try:
            # Update configuration
            self.config.update(config)
            
            # Validate configuration
            if self.config["min_confidence"] < 0 or self.config["min_confidence"] > 1:
                return ServiceOperation(
                    success=False,
                    data=None,
                    error="Invalid min_confidence value",
                    error_code="CONFIG_VALIDATION_ERROR"
                )
            
            # Initialize internal components
            self._start_time = datetime.now().timestamp()
            
            # Set status to ready
            self.set_status(ServiceStatus.READY)
            
            duration_ms = (time.time() - start_time) * 1000
            return ServiceOperation(
                success=True,
                data={
                    "service_id": self.service_id,
                    "status": self.status.value,
                    "config": self.config
                },
                duration_ms=duration_ms
            )
            
        except Exception as e:
            self.set_status(ServiceStatus.ERROR)
            return self.handle_error(e)
    
    def shutdown(self) -> ServiceOperation:
        """Gracefully shutdown service"""
        start_time = time.time()
        
        try:
            self.set_status(ServiceStatus.SHUTDOWN)
            
            # Save any pending data
            entity_count = len(self.entities)
            mention_count = len(self.mentions)
            
            # Clear data structures
            self.entities.clear()
            self.mentions.clear()
            self.surface_to_entities.clear()
            self.entity_to_mentions.clear()
            
            duration_ms = (time.time() - start_time) * 1000
            return ServiceOperation(
                success=True,
                data={
                    "entities_cleared": entity_count,
                    "mentions_cleared": mention_count
                },
                duration_ms=duration_ms
            )
            
        except Exception as e:
            return self.handle_error(e)
    
    def validate_dependencies(self) -> ServiceOperation:
        """Validate service dependencies"""
        # Identity service has no external dependencies
        return ServiceOperation(
            success=True,
            data={"dependencies": [], "all_available": True}
        )
    
    # Health check methods
    
    def _check_data_integrity(self) -> bool:
        """Check data structure integrity"""
        try:
            # Check entity-mention bidirectional mapping
            for entity_id, mention_ids in self.entity_to_mentions.items():
                if entity_id not in self.entities:
                    return False
                for mention_id in mention_ids:
                    if mention_id not in self.mentions:
                        return False
                    if self.mentions[mention_id].entity_id != entity_id:
                        return False
            
            # Check mention-entity mapping
            for mention_id, mention in self.mentions.items():
                if mention.entity_id not in self.entities:
                    return False
            
            return True
            
        except Exception:
            return False
    
    def _check_capacity(self) -> bool:
        """Check service capacity"""
        entity_usage = len(self.entities) / self.config["max_entities"]
        mention_usage = len(self.mentions) / self.config["max_mentions"]
        
        # Healthy if under 90% capacity
        return entity_usage < 0.9 and mention_usage < 0.9
    
    def _check_performance(self) -> bool:
        """Check service performance"""
        # Check if average response time is acceptable
        metrics = self.get_metrics()
        return metrics.avg_response_time < 100  # Under 100ms average
    
    # Core identity service methods (backward compatible)
    
    def create_entity(
        self, 
        canonical_name: str,
        entity_type: str,
        confidence: float = 0.9
    ) -> ServiceOperation:
        """Create a new entity
        
        Args:
            canonical_name: Primary name for the entity
            entity_type: Type of entity (PERSON, ORG, etc.)
            confidence: Confidence score
            
        Returns:
            ServiceOperation with entity data
        """
        start_time = time.time()
        
        try:
            # Validate inputs
            if not canonical_name or not entity_type:
                return ServiceOperation(
                    success=False,
                    data=None,
                    error="Invalid entity parameters",
                    error_code="INVALID_PARAMETERS"
                )
            
            # Check capacity
            if len(self.entities) >= self.config["max_entities"]:
                return ServiceOperation(
                    success=False,
                    data=None,
                    error="Entity capacity exceeded",
                    error_code="CAPACITY_EXCEEDED"
                )
            
            # Create entity
            entity_id = f"entity_{uuid.uuid4()}"
            entity = EntityInfo(
                entity_id=entity_id,
                canonical_name=canonical_name,
                entity_type=entity_type,
                confidence=confidence,
                mention_ids=[],
                created_at=datetime.now().isoformat(),
                last_updated=datetime.now().isoformat()
            )
            
            self.entities[entity_id] = entity
            self.entity_to_mentions[entity_id] = set()
            
            # Update surface form mapping
            self._update_surface_mapping(canonical_name, entity_id)
            
            duration_ms = (time.time() - start_time) * 1000
            self.track_request(duration_ms, True)
            
            return ServiceOperation(
                success=True,
                data={
                    "entity_id": entity_id,
                    "canonical_name": canonical_name,
                    "entity_type": entity_type,
                    "confidence": confidence
                },
                duration_ms=duration_ms
            )
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.track_request(duration_ms, False)
            return self.handle_error(e)
    
    def create_mention(
        self,
        surface_form: str,
        start_pos: int,
        end_pos: int,
        source_ref: str,
        entity_type: str,
        confidence: float
    ) -> ServiceOperation:
        """Create a mention and link to entity
        
        Args:
            surface_form: Text of the mention
            start_pos: Start position in source
            end_pos: End position in source
            source_ref: Reference to source document/chunk
            entity_type: Type of entity
            confidence: Confidence score
            
        Returns:
            ServiceOperation with mention and entity data
        """
        start_time = time.time()
        
        try:
            # Check capacity
            if len(self.mentions) >= self.config["max_mentions"]:
                return ServiceOperation(
                    success=False,
                    data=None,
                    error="Mention capacity exceeded",
                    error_code="CAPACITY_EXCEEDED"
                )
            
            # Find or create entity
            entity_id = self._resolve_entity(surface_form, entity_type, confidence)
            
            if not entity_id:
                # Create new entity
                entity_result = self.create_entity(surface_form, entity_type, confidence)
                if not entity_result.success:
                    return entity_result
                entity_id = entity_result.data["entity_id"]
            
            # Create mention
            mention_id = f"mention_{uuid.uuid4()}"
            mention = MentionInfo(
                mention_id=mention_id,
                entity_id=entity_id,
                surface_form=surface_form,
                source_ref=source_ref,
                start_pos=start_pos,
                end_pos=end_pos,
                confidence=confidence,
                created_at=datetime.now().isoformat()
            )
            
            self.mentions[mention_id] = mention
            self.entity_to_mentions[entity_id].add(mention_id)
            self.entities[entity_id].mention_ids.append(mention_id)
            
            duration_ms = (time.time() - start_time) * 1000
            self.track_request(duration_ms, True)
            
            return ServiceOperation(
                success=True,
                data={
                    "mention_id": mention_id,
                    "entity_id": entity_id,
                    "surface_form": surface_form,
                    "canonical_name": self.entities[entity_id].canonical_name
                },
                duration_ms=duration_ms
            )
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.track_request(duration_ms, False)
            return self.handle_error(e)
    
    def get_entity(self, entity_id: str) -> Optional[EntityInfo]:
        """Get entity by ID (backward compatible method)"""
        return self.entities.get(entity_id)
    
    def get_entity_by_mention(self, mention_id: str) -> Optional[Dict[str, Any]]:
        """Get entity information from mention ID (backward compatible)"""
        mention = self.mentions.get(mention_id)
        if mention:
            entity = self.entities.get(mention.entity_id)
            if entity:
                return {
                    "entity_id": entity.entity_id,
                    "canonical_name": entity.canonical_name,
                    "entity_type": entity.entity_type,
                    "confidence": entity.confidence
                }
        return None
    
    def resolve_surface_form(self, surface_form: str) -> List[str]:
        """Resolve surface form to entity IDs (backward compatible)"""
        return list(self.surface_to_entities.get(surface_form.lower(), set()))
    
    def merge_entities(self, entity_id1: str, entity_id2: str) -> ServiceOperation:
        """Merge two entities"""
        start_time = time.time()
        
        try:
            # Validate entities exist
            if entity_id1 not in self.entities or entity_id2 not in self.entities:
                return ServiceOperation(
                    success=False,
                    data=None,
                    error="One or both entities not found",
                    error_code="ENTITY_NOT_FOUND"
                )
            
            entity1 = self.entities[entity_id1]
            entity2 = self.entities[entity_id2]
            
            # Keep entity with higher confidence as primary
            if entity1.confidence >= entity2.confidence:
                primary_id, secondary_id = entity_id1, entity_id2
            else:
                primary_id, secondary_id = entity_id2, entity_id1
            
            # Move mentions from secondary to primary
            for mention_id in self.entity_to_mentions[secondary_id]:
                mention = self.mentions[mention_id]
                mention.entity_id = primary_id
                self.entity_to_mentions[primary_id].add(mention_id)
                self.entities[primary_id].mention_ids.append(mention_id)
            
            # Update surface mappings
            for surface_form in self._get_entity_surface_forms(secondary_id):
                self._update_surface_mapping(surface_form, primary_id)
            
            # Remove secondary entity
            del self.entities[secondary_id]
            del self.entity_to_mentions[secondary_id]
            
            # Update primary entity
            self.entities[primary_id].last_updated = datetime.now().isoformat()
            
            duration_ms = (time.time() - start_time) * 1000
            self.track_request(duration_ms, True)
            
            return ServiceOperation(
                success=True,
                data={
                    "merged_entity_id": primary_id,
                    "removed_entity_id": secondary_id,
                    "mention_count": len(self.entity_to_mentions[primary_id])
                },
                duration_ms=duration_ms
            )
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.track_request(duration_ms, False)
            return self.handle_error(e)
    
    # Helper methods
    
    def _resolve_entity(self, surface_form: str, entity_type: str, confidence: float) -> Optional[str]:
        """Resolve surface form to existing entity"""
        candidates = self.surface_to_entities.get(surface_form.lower(), set())
        
        for entity_id in candidates:
            entity = self.entities[entity_id]
            if entity.entity_type == entity_type:
                # Check if confidence is high enough to merge
                if confidence >= self.config["merge_threshold"]:
                    return entity_id
        
        return None
    
    def _update_surface_mapping(self, surface_form: str, entity_id: str):
        """Update surface form to entity mapping"""
        normalized = surface_form.lower()
        if normalized not in self.surface_to_entities:
            self.surface_to_entities[normalized] = set()
        self.surface_to_entities[normalized].add(entity_id)
    
    def _get_entity_surface_forms(self, entity_id: str) -> Set[str]:
        """Get all surface forms for an entity"""
        surface_forms = set()
        for mention_id in self.entity_to_mentions.get(entity_id, set()):
            mention = self.mentions.get(mention_id)
            if mention:
                surface_forms.add(mention.surface_form.lower())
        return surface_forms
    
    # Statistics and reporting
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get service statistics"""
        entity_type_counts = {}
        for entity in self.entities.values():
            entity_type_counts[entity.entity_type] = entity_type_counts.get(entity.entity_type, 0) + 1
        
        return {
            "total_entities": len(self.entities),
            "total_mentions": len(self.mentions),
            "unique_surface_forms": len(self.surface_to_entities),
            "entity_type_distribution": entity_type_counts,
            "avg_mentions_per_entity": len(self.mentions) / max(1, len(self.entities))
        }


# Factory function for backward compatibility
def create_identity_service() -> IdentityServiceUnified:
    """Create and initialize identity service
    
    Returns:
        Configured IdentityServiceUnified instance
    """
    service = IdentityServiceUnified()
    service.initialize({})
    return service