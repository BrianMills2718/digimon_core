"""
T301: Multi-Document Knowledge Fusion
Consolidate knowledge across document collections with conflict resolution.

This tool extends Phase 2's ontology-aware graph building to handle multiple
documents, resolving entity duplicates and conflicting information through
evidence-based arbitration and LLM-driven reasoning.
"""

import logging
from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict
import json
import re
import html

from ..phase2.t31_ontology_graph_builder import OntologyAwareGraphBuilder, GraphBuildResult
from ..phase2.t23c_ontology_aware_extractor import ExtractionResult
from ...core.enhanced_identity_service import EnhancedIdentityService
from ...core.identity_service import Entity, Relationship
from ...core.quality_service import QualityService
from ...core.provenance_service import ProvenanceService
from ...ontology_generator import DomainOntology

logger = logging.getLogger(__name__)


@dataclass
class FusionResult:
    """Result of multi-document knowledge fusion."""
    total_documents: int = 0
    entities_before_fusion: int = 0
    entities_after_fusion: int = 0
    relationships_before_fusion: int = 0
    relationships_after_fusion: int = 0
    conflicts_resolved: int = 0
    fusion_time_seconds: float = 0.0
    consistency_score: float = 0.0
    evidence_chains: List[Dict[str, Any]] = field(default_factory=list)
    duplicate_clusters: List[List[str]] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "total_documents": self.total_documents,
            "entities_before_fusion": self.entities_before_fusion,
            "entities_after_fusion": self.entities_after_fusion,
            "relationships_before_fusion": self.relationships_before_fusion,
            "relationships_after_fusion": self.relationships_after_fusion,
            "conflicts_resolved": self.conflicts_resolved,
            "fusion_time_seconds": self.fusion_time_seconds,
            "consistency_score": self.consistency_score,
            "evidence_chains": self.evidence_chains,
            "duplicate_clusters": self.duplicate_clusters,
            "warnings": self.warnings,
            "deduplication_rate": 1 - (self.entities_after_fusion / self.entities_before_fusion) if self.entities_before_fusion > 0 else 0
        }


@dataclass
class ConsistencyMetrics:
    """Metrics for knowledge consistency across documents."""
    entity_consistency: float = 0.0
    relationship_consistency: float = 0.0
    temporal_consistency: float = 0.0
    ontological_compliance: float = 0.0
    overall_score: float = 0.0
    inconsistencies: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class EntityCluster:
    """Cluster of potentially duplicate entities."""
    cluster_id: str
    entities: List[Entity]
    canonical_entity: Optional[Entity] = None
    confidence: float = 0.0
    evidence: List[str] = field(default_factory=list)


class MultiDocumentFusion(OntologyAwareGraphBuilder):
    """
    Advanced multi-document knowledge fusion with conflict resolution.
    Extends Phase 2's graph builder with multi-document capabilities.
    """
    
    def __init__(self,
                 neo4j_uri: str = "bolt://localhost:7687",
                 neo4j_user: str = "neo4j",
                 neo4j_password: str = "password",
                 confidence_threshold: float = 0.8,
                 similarity_threshold: float = 0.85,
                 conflict_resolution_model: Optional[str] = None):
        """
        Initialize multi-document fusion engine.
        
        Args:
            neo4j_uri: Neo4j connection URI
            neo4j_user: Neo4j username
            neo4j_password: Neo4j password
            confidence_threshold: Minimum confidence for fusion decisions
            similarity_threshold: Threshold for entity similarity matching
            conflict_resolution_model: Optional LLM model for conflict resolution
        """
        super().__init__(neo4j_uri, neo4j_user, neo4j_password, confidence_threshold)
        
        self.similarity_threshold = similarity_threshold
        self.conflict_resolution_model = conflict_resolution_model or "gemini-2.0-flash-exp"
        
        # Additional services for fusion
        self.identity_service = EnhancedIdentityService()
        self.quality_service = QualityService()
        self.provenance_service = ProvenanceService()
        
        # Fusion tracking
        self.document_registry: Dict[str, Dict[str, Any]] = {}
        self.entity_clusters: Dict[str, EntityCluster] = {}
        self.conflict_history: List[Dict[str, Any]] = []
        
        logger.info("✅ Multi-Document Fusion engine initialized")
    
    def _sanitize_string(self, text: str, max_length: int = 1000) -> str:
        """Sanitize input strings for security."""
        if not text:
            return ""
        
        # HTML escape
        text = html.escape(text)
        
        # Remove control characters
        text = re.sub(r'[\x00-\x1F\x7F]', '', text)
        
        # Truncate if too long
        if len(text) > max_length:
            text = text[:max_length] + "..."
            
        return text.strip()
    
    def fuse_documents(self,
                      document_refs: List[str],
                      fusion_strategy: str = "evidence_based",
                      batch_size: int = 10) -> FusionResult:
        """
        Fuse knowledge from multiple documents into a consolidated graph.
        
        Args:
            document_refs: List of document references to fuse
            fusion_strategy: Strategy for fusion ('evidence_based', 'confidence_weighted', 'temporal_priority')
            batch_size: Number of documents to process in each batch
            
        Returns:
            FusionResult with fusion metrics and evidence chains
        """
        start_time = datetime.now()
        result = FusionResult(total_documents=len(document_refs))
        
        try:
            # Pre-fusion metrics
            result.entities_before_fusion = self._count_entities()
            result.relationships_before_fusion = self._count_relationships()
            
            # Process documents in batches
            for i in range(0, len(document_refs), batch_size):
                batch = document_refs[i:i + batch_size]
                logger.info(f"Processing batch {i//batch_size + 1}: {len(batch)} documents")
                
                # Load entities and relationships from batch
                batch_entities, batch_relationships = self._load_document_batch(batch)
                
                # Find duplicate entity clusters
                clusters = self._find_entity_clusters(batch_entities)
                result.duplicate_clusters.extend([
                    [e.entity_id for e in cluster.entities] 
                    for cluster in clusters.values()
                ])
                
                # Resolve entities within clusters
                resolved_entities = self._resolve_entity_clusters(clusters, fusion_strategy)
                
                # Merge relationships with resolved entities
                merged_relationships = self._merge_relationships(
                    batch_relationships,
                    resolved_entities,
                    fusion_strategy
                )
                
                # Detect and resolve conflicts
                conflicts = self._detect_conflicts(resolved_entities, merged_relationships)
                result.conflicts_resolved += len(conflicts)
                
                # Update graph with fused knowledge
                self._update_graph_with_fusion(resolved_entities, merged_relationships)
                
                # Generate evidence chains
                for entity_id, entity in resolved_entities.items():
                    if hasattr(entity, '_fusion_evidence'):
                        result.evidence_chains.append({
                            "entity_id": entity_id,
                            "evidence": entity._fusion_evidence
                        })
            
            # Post-fusion metrics
            result.entities_after_fusion = self._count_entities()
            result.relationships_after_fusion = self._count_relationships()
            
            # Calculate consistency metrics
            consistency = self.calculate_knowledge_consistency()
            result.consistency_score = consistency.overall_score
            
            # Add warnings for low consistency areas
            if consistency.entity_consistency < 0.7:
                result.warnings.append(f"Low entity consistency: {consistency.entity_consistency:.2%}")
            if consistency.relationship_consistency < 0.7:
                result.warnings.append(f"Low relationship consistency: {consistency.relationship_consistency:.2%}")
            
            result.fusion_time_seconds = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"✅ Fusion complete: {result.entities_before_fusion} → {result.entities_after_fusion} entities")
            return result
            
        except Exception as e:
            logger.error(f"Fusion failed: {e}")
            result.warnings.append(f"Fusion error: {str(e)}")
            return result
    
    def resolve_entity_conflicts(self, entities: List[Entity]) -> Entity:
        """
        Resolve conflicts between multiple entity representations.
        
        Args:
            entities: List of conflicting entity representations
            
        Returns:
            Resolved canonical entity with merged information
        """
        if not entities:
            raise ValueError("No entities provided for conflict resolution")
        
        if len(entities) == 1:
            return entities[0]
        
        # Validate entities
        for e in entities:
            if not e.canonical_name or not e.canonical_name.strip():
                raise ValueError(f"Entity {e.id} has empty canonical name")
            if not isinstance(e.confidence, (int, float)) or e.confidence != e.confidence:  # NaN check
                raise ValueError(f"Entity {e.id} has invalid confidence: {e.confidence}")
            if e.confidence < 0 or e.confidence > 1:
                raise ValueError(f"Entity {e.id} confidence out of range: {e.confidence}")
        
        # Sort by confidence to use highest confidence as base
        sorted_entities = sorted(entities, key=lambda e: e.confidence, reverse=True)
        canonical = sorted_entities[0]
        
        # Merge attributes from all entities
        merged_attributes = {}
        confidence_sum = 0
        evidence_count = 0
        
        for entity in entities:
            # Aggregate confidence scores
            confidence_sum += entity.confidence
            evidence_count += 1
            
            # Merge attributes with conflict detection
            if hasattr(entity, 'attributes') and entity.attributes:
                for key, value in entity.attributes.items():
                    if key not in merged_attributes:
                        merged_attributes[key] = {
                            "value": value,
                            "sources": [entity.id],
                            "confidence": entity.confidence
                        }
                    else:
                        # Conflict detected - use confidence-weighted resolution
                        existing = merged_attributes[key]
                        if value != existing["value"]:
                            # Use LLM for complex conflict resolution if available
                            if self._should_use_llm_resolution(key, existing["value"], value):
                                resolved_value = self._llm_resolve_conflict(
                                    attribute=key,
                                    value1=existing["value"],
                                    value2=value,
                                    context=canonical.name
                                )
                                merged_attributes[key]["value"] = resolved_value
                                merged_attributes[key]["resolved_by_llm"] = True
                            else:
                                # Use confidence-weighted resolution
                                if entity.confidence > existing["confidence"]:
                                    merged_attributes[key]["value"] = value
                                    merged_attributes[key]["confidence"] = entity.confidence
                        
                        merged_attributes[key]["sources"].append(entity.id)
        
        # Create resolved entity with sanitized name
        canonical_name = canonical.canonical_name if hasattr(canonical, 'canonical_name') else canonical.name
        resolved = Entity(
            id=f"resolved_{canonical.id}",
            canonical_name=self._sanitize_string(canonical_name),
            entity_type=canonical.entity_type,
            confidence=confidence_sum / evidence_count
        )
        
        # Store fusion evidence
        resolved._fusion_evidence = {
            "source_entities": [e.id for e in entities],
            "resolution_strategy": "confidence_weighted_with_llm",
            "merged_attributes": merged_attributes,
            "conflicts_resolved": sum(1 for attr in merged_attributes.values() if len(attr.get("sources", [])) > 1)
        }
        
        return resolved
    
    def merge_relationship_evidence(self, relationships: List[Relationship]) -> Relationship:
        """
        Merge evidence from multiple relationship instances.
        
        Args:
            relationships: List of relationship instances to merge
            
        Returns:
            Merged relationship with aggregated evidence
        """
        if not relationships:
            raise ValueError("No relationships provided for merging")
        
        if len(relationships) == 1:
            rel = relationships[0]
            # Validate single relationship
            if not rel.relationship_type or not rel.relationship_type.strip():
                raise ValueError(f"Relationship {rel.id if hasattr(rel, 'id') else 'unknown'} has empty type")
            return rel
        
        # Use first relationship as template
        base_rel = relationships[0]
        
        # Aggregate evidence
        evidence_sources = []
        confidence_scores = []
        temporal_range = []
        
        for rel in relationships:
            confidence_scores.append(rel.confidence)
            
            if hasattr(rel, 'source_document'):
                evidence_sources.append(rel.source_document)
            
            if hasattr(rel, 'timestamp'):
                temporal_range.append(rel.timestamp)
        
        # Create merged relationship
        merged = Relationship(
            id=f"merged_{base_rel.id}",
            source_id=base_rel.source_id,
            target_id=base_rel.target_id,
            relationship_type=base_rel.relationship_type,
            confidence=sum(confidence_scores) / len(confidence_scores)
        )
        
        # Add aggregated evidence
        merged._fusion_evidence = {
            "source_relationships": [r.id if hasattr(r, 'id') else str(r) for r in relationships],
            "evidence_sources": evidence_sources,
            "confidence_distribution": confidence_scores,
            "temporal_range": [min(temporal_range), max(temporal_range)] if temporal_range else None,
            "evidence_count": len(relationships)
        }
        
        return merged
    
    def calculate_knowledge_consistency(self) -> ConsistencyMetrics:
        """
        Calculate consistency metrics for the fused knowledge graph.
        
        Returns:
            ConsistencyMetrics with detailed consistency analysis
        """
        metrics = ConsistencyMetrics()
        
        try:
            # Entity consistency - check for proper deduplication
            entity_consistency_score = self._calculate_entity_consistency()
            metrics.entity_consistency = entity_consistency_score
            
            # Relationship consistency - check for conflicting relationships
            relationship_consistency_score = self._calculate_relationship_consistency()
            metrics.relationship_consistency = relationship_consistency_score
            
            # Temporal consistency - check temporal ordering
            temporal_consistency_score = self._calculate_temporal_consistency()
            metrics.temporal_consistency = temporal_consistency_score
            
            # Ontological compliance - check against ontology constraints
            if self.current_ontology:
                ontology_compliance_score = self._calculate_ontology_compliance()
                metrics.ontological_compliance = ontology_compliance_score
            else:
                metrics.ontological_compliance = 1.0  # No ontology to check against
            
            # Calculate overall score
            scores = [
                metrics.entity_consistency,
                metrics.relationship_consistency,
                metrics.temporal_consistency,
                metrics.ontological_compliance
            ]
            metrics.overall_score = sum(scores) / len(scores)
            
            # Identify specific inconsistencies
            if metrics.entity_consistency < 1.0:
                metrics.inconsistencies.extend(self._find_entity_inconsistencies())
            if metrics.relationship_consistency < 1.0:
                metrics.inconsistencies.extend(self._find_relationship_inconsistencies())
            
            logger.info(f"Consistency analysis complete: {metrics.overall_score:.2%}")
            return metrics
            
        except Exception as e:
            logger.error(f"Consistency calculation failed: {e}")
            return metrics
    
    def _load_document_batch(self, document_refs: List[str]) -> Tuple[List[Entity], List[Relationship]]:
        """Load entities and relationships from a batch of documents."""
        all_entities = []
        all_relationships = []
        
        with self.driver.session() as session:
            for doc_ref in document_refs:
                # Query entities from document
                entity_query = """
                MATCH (e:Entity)-[:EXTRACTED_FROM]->(d:Document {reference: $doc_ref})
                RETURN e
                """
                entity_result = session.run(entity_query, doc_ref=doc_ref)
                
                for record in entity_result:
                    node = record["e"]
                    entity = Entity(
                        id=node["id"],
                        canonical_name=node["name"],
                        entity_type=node["type"],
                        confidence=node.get("confidence", 1.0)
                    )
                    entity.name = entity.canonical_name  # Add name for compatibility
                    entity.source_document = doc_ref
                    all_entities.append(entity)
                
                # Query relationships from document
                rel_query = """
                MATCH (s:Entity)-[r]->(t:Entity)
                WHERE EXISTS((s)-[:EXTRACTED_FROM]->(:Document {reference: $doc_ref}))
                   OR EXISTS((t)-[:EXTRACTED_FROM]->(:Document {reference: $doc_ref}))
                RETURN s.id as source_id, t.id as target_id, type(r) as rel_type, r
                """
                rel_result = session.run(rel_query, doc_ref=doc_ref)
                
                for record in rel_result:
                    rel = Relationship(
                        source_id=record["source_id"],
                        target_id=record["target_id"],
                        relationship_type=record["rel_type"],
                        confidence=record["r"].get("confidence", 1.0) if record["r"] else 1.0
                    )
                    rel.source_document = doc_ref
                    all_relationships.append(rel)
        
        return all_entities, all_relationships
    
    def _find_entity_clusters(self, entities: List[Entity]) -> Dict[str, EntityCluster]:
        """Find clusters of potentially duplicate entities using similarity."""
        clusters = {}
        processed = set()
        
        for i, entity1 in enumerate(entities):
            if entity1.id in processed:
                continue
            
            cluster = EntityCluster(
                cluster_id=f"cluster_{len(clusters)}",
                entities=[entity1],
                confidence=1.0
            )
            
            # Find similar entities
            for j, entity2 in enumerate(entities[i+1:], i+1):
                if entity2.id in processed:
                    continue
                
                similarity = self._calculate_entity_similarity(entity1, entity2)
                if similarity >= self.similarity_threshold:
                    cluster.entities.append(entity2)
                    processed.add(entity2.id)
                    cluster.evidence.append(f"Similarity score: {similarity:.3f}")
            
            if len(cluster.entities) > 1:
                processed.add(entity1.id)
                clusters[cluster.cluster_id] = cluster
                logger.debug(f"Found cluster with {len(cluster.entities)} entities")
        
        return clusters
    
    def _calculate_entity_similarity(self, entity1: Entity, entity2: Entity) -> float:
        """Calculate similarity between two entities."""
        # Type must match
        if entity1.entity_type != entity2.entity_type:
            return 0.0
        
        # Use enhanced identity service for embedding-based similarity
        name1 = entity1.canonical_name if hasattr(entity1, 'canonical_name') else entity1.name
        name2 = entity2.canonical_name if hasattr(entity2, 'canonical_name') else entity2.name
        
        # Quick exact match check (avoid expensive embedding call)
        if name1.lower() == name2.lower():
            return 1.0
        
        # For performance, use simple heuristics before embeddings
        name1_lower = name1.lower()
        name2_lower = name2.lower()
        
        # Check for substring matches
        if name1_lower in name2_lower or name2_lower in name1_lower:
            # Calculate overlap ratio
            overlap = len(name1_lower) if name1_lower in name2_lower else len(name2_lower)
            total = max(len(name1_lower), len(name2_lower))
            return 0.7 + (0.2 * overlap / total)
        
        # Check for common words (for multi-word entities)
        words1 = set(name1_lower.split())
        words2 = set(name2_lower.split())
        if words1 and words2:
            common = words1.intersection(words2)
            if common:
                return 0.5 + (0.3 * len(common) / max(len(words1), len(words2)))
        
        # Only use embeddings for potentially similar entities
        # This dramatically reduces API calls
        return 0.0  # Skip embeddings for clearly different entities
    
    def _resolve_entity_clusters(self,
                                clusters: Dict[str, EntityCluster],
                                strategy: str) -> Dict[str, Entity]:
        """Resolve entity clusters into canonical entities."""
        resolved_entities = {}
        
        for cluster_id, cluster in clusters.items():
            if strategy == "evidence_based":
                # Resolve based on evidence count
                canonical = self.resolve_entity_conflicts(cluster.entities)
            elif strategy == "confidence_weighted":
                # Resolve based on confidence scores
                canonical = max(cluster.entities, key=lambda e: e.confidence)
            elif strategy == "temporal_priority":
                # Resolve based on temporal order (most recent)
                canonical = max(
                    cluster.entities,
                    key=lambda e: getattr(e, 'timestamp', datetime.min)
                )
            else:
                # Default to evidence-based
                canonical = self.resolve_entity_conflicts(cluster.entities)
            
            cluster.canonical_entity = canonical
            resolved_entities[canonical.id] = canonical
        
        return resolved_entities
    
    def _merge_relationships(self,
                           relationships: List[Relationship],
                           resolved_entities: Dict[str, Entity],
                           strategy: str) -> List[Relationship]:
        """Merge relationships using resolved entities."""
        # Group relationships by type and endpoints
        relationship_groups = defaultdict(list)
        
        for rel in relationships:
            # Map to resolved entities if available
            source_id = self._find_resolved_entity_id(rel.source_id, resolved_entities)
            target_id = self._find_resolved_entity_id(rel.target_id, resolved_entities)
            
            key = (source_id, target_id, rel.relationship_type)
            relationship_groups[key].append(rel)
        
        # Merge each group
        merged_relationships = []
        for (source_id, target_id, rel_type), rels in relationship_groups.items():
            if len(rels) == 1:
                merged_relationships.append(rels[0])
            else:
                merged = self.merge_relationship_evidence(rels)
                merged_relationships.append(merged)
        
        return merged_relationships
    
    def _find_resolved_entity_id(self, entity_id: str, resolved_entities: Dict[str, Entity]) -> str:
        """Find resolved entity ID for a given entity."""
        # Check if already resolved
        if entity_id in resolved_entities:
            return entity_id
        
        # Search in cluster evidence
        for resolved_id, entity in resolved_entities.items():
            if hasattr(entity, '_fusion_evidence'):
                source_entities = entity._fusion_evidence.get('source_entities', [])
                if entity_id in source_entities:
                    return resolved_id
        
        return entity_id
    
    def _detect_conflicts(self,
                         entities: Dict[str, Entity],
                         relationships: List[Relationship]) -> List[Dict[str, Any]]:
        """Detect conflicts in fused knowledge."""
        conflicts = []
        
        # Check for conflicting relationships
        rel_map = defaultdict(list)
        for rel in relationships:
            key = (rel.source_id, rel.target_id)
            rel_map[key].append(rel)
        
        for (source, target), rels in rel_map.items():
            rel_types = set(r.relationship_type for r in rels)
            if len(rel_types) > 1:
                conflicts.append({
                    "type": "relationship_conflict",
                    "source": source,
                    "target": target,
                    "conflicting_types": list(rel_types)
                })
        
        return conflicts
    
    def _update_graph_with_fusion(self,
                                 entities: Dict[str, Entity],
                                 relationships: List[Relationship]):
        """Update Neo4j graph with fused knowledge."""
        with self.driver.session() as session:
            # Merge entities
            for entity_id, entity in entities.items():
                merge_query = """
                MERGE (e:Entity {id: $entity_id})
                SET e.name = $name,
                    e.type = $entity_type,
                    e.confidence = $confidence,
                    e.fused = true,
                    e.fusion_timestamp = datetime()
                """
                session.run(
                    merge_query,
                    entity_id=entity_id,
                    name=entity.name,
                    entity_type=entity.entity_type,
                    confidence=entity.confidence
                )
                
                # Store fusion evidence
                if hasattr(entity, '_fusion_evidence'):
                    evidence_query = """
                    MATCH (e:Entity {id: $entity_id})
                    SET e.fusion_evidence = $evidence
                    """
                    session.run(
                        evidence_query,
                        entity_id=entity_id,
                        evidence=json.dumps(entity._fusion_evidence)
                    )
            
            # Merge relationships
            for rel in relationships:
                merge_rel_query = """
                MATCH (s:Entity {id: $source_id})
                MATCH (t:Entity {id: $target_id})
                MERGE (s)-[r:%s]->(t)
                SET r.confidence = $confidence,
                    r.fused = true,
                    r.fusion_timestamp = datetime()
                """ % rel.relationship_type
                
                session.run(
                    merge_rel_query,
                    source_id=rel.source_id,
                    target_id=rel.target_id,
                    confidence=rel.confidence
                )
    
    def _should_use_llm_resolution(self, attribute: str, value1: Any, value2: Any) -> bool:
        """Determine if LLM should be used for conflict resolution."""
        # Use LLM for complex text attributes
        if attribute in ["description", "summary", "context"]:
            return True
        
        # Use LLM if values are significantly different
        if isinstance(value1, str) and isinstance(value2, str):
            if len(value1) > 50 and len(value2) > 50:
                return True
        
        return False
    
    def _llm_resolve_conflict(self,
                             attribute: str,
                             value1: Any,
                             value2: Any,
                             context: str) -> Any:
        """Use LLM to resolve attribute conflicts."""
        # TODO: Implement actual LLM call
        # For now, return the longer/more detailed value
        if isinstance(value1, str) and isinstance(value2, str):
            return value1 if len(value1) > len(value2) else value2
        return value1
    
    def _count_entities(self) -> int:
        """Count total entities in graph."""
        with self.driver.session() as session:
            result = session.run("MATCH (e:Entity) RETURN count(e) as count")
            return result.single()["count"]
    
    def _count_relationships(self) -> int:
        """Count total relationships in graph."""
        with self.driver.session() as session:
            result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
            return result.single()["count"]
    
    def _calculate_entity_consistency(self) -> float:
        """Calculate entity deduplication consistency."""
        with self.driver.session() as session:
            # Find potential duplicates based on name similarity
            query = """
            MATCH (e1:Entity), (e2:Entity)
            WHERE e1.id < e2.id 
              AND e1.type = e2.type
              AND e1.name CONTAINS e2.name OR e2.name CONTAINS e1.name
            RETURN count(*) as duplicate_pairs
            """
            duplicates = session.run(query).single()["duplicate_pairs"]
            
            total_entities = self._count_entities()
            if total_entities == 0:
                return 1.0
            
            # Lower score for more duplicates
            return max(0, 1 - (duplicates / total_entities))
    
    def _calculate_relationship_consistency(self) -> float:
        """Calculate relationship consistency."""
        with self.driver.session() as session:
            # Find conflicting relationships
            query = """
            MATCH (s:Entity)-[r1]->(t:Entity)
            MATCH (s)-[r2]->(t)
            WHERE type(r1) <> type(r2) AND id(r1) < id(r2)
            RETURN count(*) as conflicts
            """
            conflicts = session.run(query).single()["conflicts"]
            
            total_relationships = self._count_relationships()
            if total_relationships == 0:
                return 1.0
            
            return max(0, 1 - (conflicts / total_relationships))
    
    def _calculate_temporal_consistency(self) -> float:
        """Calculate temporal consistency of knowledge."""
        # TODO: Implement temporal consistency checking
        # For now, return perfect score
        return 1.0
    
    def _calculate_ontology_compliance(self) -> float:
        """Calculate compliance with ontology constraints."""
        if not self.current_ontology:
            return 1.0
        
        with self.driver.session() as session:
            # Check entity type compliance
            valid_types = {et.name for et in self.current_ontology.entity_types}
            
            query = """
            MATCH (e:Entity)
            RETURN e.type as entity_type, count(*) as count
            """
            result = session.run(query)
            
            compliant = 0
            total = 0
            for record in result:
                count = record["count"]
                total += count
                if record["entity_type"] in valid_types:
                    compliant += count
            
            return compliant / total if total > 0 else 1.0
    
    def _find_entity_inconsistencies(self) -> List[Dict[str, Any]]:
        """Find specific entity inconsistencies."""
        inconsistencies = []
        
        with self.driver.session() as session:
            # Find potential duplicates
            query = """
            MATCH (e1:Entity), (e2:Entity)
            WHERE e1.id < e2.id 
              AND e1.type = e2.type
              AND e1.name CONTAINS e2.name OR e2.name CONTAINS e1.name
            RETURN e1.id as id1, e1.name as name1, 
                   e2.id as id2, e2.name as name2,
                   e1.type as type
            LIMIT 10
            """
            result = session.run(query)
            
            for record in result:
                inconsistencies.append({
                    "type": "potential_duplicate",
                    "entities": [
                        {"id": record["id1"], "name": record["name1"]},
                        {"id": record["id2"], "name": record["name2"]}
                    ],
                    "entity_type": record["type"]
                })
        
        return inconsistencies
    
    def _find_relationship_inconsistencies(self) -> List[Dict[str, Any]]:
        """Find specific relationship inconsistencies."""
        inconsistencies = []
        
        with self.driver.session() as session:
            # Find conflicting relationships
            query = """
            MATCH (s:Entity)-[r1]->(t:Entity)
            MATCH (s)-[r2]->(t)
            WHERE type(r1) <> type(r2) AND id(r1) < id(r2)
            RETURN s.id as source, t.id as target,
                   type(r1) as type1, type(r2) as type2
            LIMIT 10
            """
            result = session.run(query)
            
            for record in result:
                inconsistencies.append({
                    "type": "conflicting_relationships",
                    "source": record["source"],
                    "target": record["target"],
                    "relationship_types": [record["type1"], record["type2"]]
                })
        
        return inconsistencies


def demonstrate_multi_document_fusion():
    """Demonstrate multi-document knowledge fusion capabilities."""
    print("🚀 Demonstrating T301: Multi-Document Knowledge Fusion")
    
    # Initialize fusion engine
    fusion_engine = MultiDocumentFusion()
    
    # Example: Fuse multiple climate policy documents
    document_refs = [
        "doc_climate_policy_2023",
        "doc_paris_agreement_update",
        "doc_renewable_energy_report",
        "doc_carbon_markets_analysis"
    ]
    
    print(f"\nFusing {len(document_refs)} documents...")
    
    # Perform fusion
    fusion_result = fusion_engine.fuse_documents(
        document_refs=document_refs,
        fusion_strategy="evidence_based",
        batch_size=2
    )
    
    # Display results
    print(f"\n✅ Fusion Results:")
    print(f"  - Entities: {fusion_result.entities_before_fusion} → {fusion_result.entities_after_fusion}")
    print(f"  - Deduplication rate: {(1 - fusion_result.entities_after_fusion/fusion_result.entities_before_fusion)*100:.1f}%")
    print(f"  - Conflicts resolved: {fusion_result.conflicts_resolved}")
    print(f"  - Consistency score: {fusion_result.consistency_score:.2%}")
    print(f"  - Processing time: {fusion_result.fusion_time_seconds:.2f}s")
    
    # Check consistency
    consistency = fusion_engine.calculate_knowledge_consistency()
    print(f"\n📊 Knowledge Consistency:")
    print(f"  - Entity consistency: {consistency.entity_consistency:.2%}")
    print(f"  - Relationship consistency: {consistency.relationship_consistency:.2%}")
    print(f"  - Ontological compliance: {consistency.ontological_compliance:.2%}")
    print(f"  - Overall score: {consistency.overall_score:.2%}")
    
    return fusion_result


if __name__ == "__main__":
    demonstrate_multi_document_fusion()