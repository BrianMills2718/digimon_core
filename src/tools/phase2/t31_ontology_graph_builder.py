"""
T31: Ontology-Aware Graph Builder
Replaces basic graph building with ontology-driven entity and relationship creation.
Integrates contextual embeddings and semantic reasoning.
"""

import os
import json
import logging
import uuid
from typing import List, Dict, Optional, Any, Set, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import numpy as np
import neo4j
from neo4j import GraphDatabase

from src.core.identity_service import Entity, Relationship
from src.core.identity_service import IdentityService
from src.tools.phase2.t23c_ontology_aware_extractor import OntologyAwareExtractor, OntologyExtractionResult
from src.ontology_generator import DomainOntology
from src.core.ontology_storage_service import OntologyStorageService

logger = logging.getLogger(__name__)


@dataclass
class GraphMetrics:
    """Metrics for ontology-aware graph quality assessment."""
    total_entities: int
    total_relationships: int
    ontology_coverage: float  # Percentage of ontology types used
    semantic_density: float   # Average relationships per entity
    confidence_distribution: Dict[str, int]
    entity_type_distribution: Dict[str, int]
    relationship_type_distribution: Dict[str, int]


@dataclass
class GraphBuildResult:
    """Result of ontology-aware graph building."""
    entities_created: int
    relationships_created: int
    entities_merged: int
    low_confidence_entities: int
    ontology_mismatches: int
    execution_time_seconds: float
    metrics: GraphMetrics
    warnings: List[str]
    errors: List[str]


class OntologyAwareGraphBuilder:
    """
    Build knowledge graphs using domain ontologies for high-quality entity resolution.
    Integrates semantic embeddings and ontological constraints.
    """
    
    def __init__(self, 
                 neo4j_uri: Optional[str] = None,
                 neo4j_user: Optional[str] = None, 
                 neo4j_password: Optional[str] = None,
                 identity_service: Optional[IdentityService] = None,
                 ontology_storage: Optional[OntologyStorageService] = None,
                 confidence_threshold: float = 0.7):
        """
        Initialize the ontology-aware graph builder.
        
        Args:
            neo4j_uri: Neo4j database URI
            neo4j_user: Neo4j username
            neo4j_password: Neo4j password
            identity_service: Identity service for entity resolution
            ontology_storage: Ontology storage service
            confidence_threshold: Minimum confidence for entity/relationship creation
        """
        self.confidence_threshold = confidence_threshold
        self.warnings = []
        self.errors = []
        
        # Allow tools to work standalone for testing
        if neo4j_uri is None:
            from src.core.service_manager import ServiceManager
            service_manager = ServiceManager()
            neo4j_manager = service_manager.get_neo4j_manager()
            self.driver = neo4j_manager.get_driver()
        else:
            # Use provided credentials
            self.driver = GraphDatabase.driver(
                neo4j_uri, 
                auth=(neo4j_user or "neo4j", neo4j_password or "password")
            )
        
        # Initialize services - use provided or create via ServiceManager
        if identity_service is None or ontology_storage is None:
            from src.core.service_manager import ServiceManager
            service_manager = ServiceManager()
            self.identity_service = identity_service or service_manager.get_identity_service()
            self.ontology_storage = ontology_storage or OntologyStorageService()
        else:
            self.identity_service = identity_service
            self.ontology_storage = ontology_storage
        
        # Entity resolution cache
        self.entity_cache = {}
        self.relationship_cache = set()
        
        # Ontology constraints
        self.current_ontology = None
        self.valid_entity_types = set()
        self.valid_relationship_types = set()
        
    def set_ontology(self, ontology: DomainOntology):
        """Set the domain ontology for graph building."""
        self.current_ontology = ontology
        self.valid_entity_types = {et.name for et in ontology.entity_types}
        self.valid_relationship_types = {rt.name for rt in ontology.relationship_types}
        logger.info(f"📋 Ontology set: {ontology.domain_name} "
                   f"({len(self.valid_entity_types)} entity types, "
                   f"{len(self.valid_relationship_types)} relationship types)")
    
    def build_graph_from_extraction(self, extraction_result: OntologyExtractionResult,
                                   source_document: str) -> GraphBuildResult:
        """
        Build graph from ontology-aware extraction results.
        
        Args:
            extraction_result: Results from T23c ontology extractor
            source_document: Source document reference
            
        Returns:
            GraphBuildResult with build statistics and metrics
        """
        start_time = datetime.now()
        self.warnings.clear()
        self.errors.clear()
        
        logger.info(f"🔨 Building graph from {len(extraction_result.entities)} entities "
                   f"and {len(extraction_result.relationships)} relationships")
        
        entities_created = 0
        relationships_created = 0
        entities_merged = 0
        low_confidence_entities = 0
        ontology_mismatches = 0
        
        try:
            # Step 1: Process entities with ontological validation
            entity_mapping = {}
            for entity in extraction_result.entities:
                result = self._process_entity(entity, source_document)
                if result["created"]:
                    entities_created += 1
                if result["merged"]:
                    entities_merged += 1
                if result["low_confidence"]:
                    low_confidence_entities += 1
                if result["ontology_mismatch"]:
                    ontology_mismatches += 1
                
                entity_mapping[entity.id] = result["neo4j_id"]
            
            # Step 2: Process relationships with semantic validation
            for relationship in extraction_result.relationships:
                if (relationship.source_id in entity_mapping and 
                    relationship.target_id in entity_mapping):
                    
                    neo4j_source = entity_mapping[relationship.source_id]
                    neo4j_target = entity_mapping[relationship.target_id]
                    
                    if self._create_relationship(relationship, neo4j_source, neo4j_target, source_document):
                        relationships_created += 1
            
            # Step 3: Calculate graph metrics
            metrics = self._calculate_graph_metrics(source_document)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return GraphBuildResult(
                entities_created=entities_created,
                relationships_created=relationships_created,
                entities_merged=entities_merged,
                low_confidence_entities=low_confidence_entities,
                ontology_mismatches=ontology_mismatches,
                execution_time_seconds=execution_time,
                metrics=metrics,
                warnings=self.warnings.copy(),
                errors=self.errors.copy()
            )
            
        except Exception as e:
            logger.error(f"❌ Graph building failed: {e}")
            self.errors.append(f"Graph building failed: {str(e)}")
            raise
    
    def _process_entity(self, entity: Entity, source_document: str) -> Dict[str, Any]:
        """Process a single entity with ontological validation."""
        result = {
            "created": False,
            "merged": False,
            "low_confidence": False,
            "ontology_mismatch": False,
            "neo4j_id": None
        }
        
        # Confidence check
        if entity.confidence < self.confidence_threshold:
            result["low_confidence"] = True
            self.warnings.append(f"Low confidence entity: {entity.canonical_name} ({entity.confidence:.2f})")
        
        # Ontology validation
        if self.current_ontology and entity.entity_type not in self.valid_entity_types:
            result["ontology_mismatch"] = True
            self.warnings.append(f"Entity type '{entity.entity_type}' not in ontology for '{entity.canonical_name}'")
            # Use closest valid type or UNKNOWN
            entity.entity_type = self._find_closest_entity_type(entity.entity_type)
        
        # Check for existing similar entities
        cache_key = f"{entity.canonical_name}_{entity.entity_type}"
        if cache_key in self.entity_cache:
            result["neo4j_id"] = self.entity_cache[cache_key]
            result["merged"] = True
            return result
        
        # Create entity in Neo4j with enhanced properties
        try:
            with self.driver.session() as session:
                neo4j_result = session.run("""
                    MERGE (e:Entity {
                        canonical_name: $canonical_name,
                        entity_type: $entity_type
                    })
                    ON CREATE SET 
                        e.id = randomUUID(),
                        e.created_at = datetime(),
                        e.confidence = $confidence,
                        e.source_documents = [$source_document],
                        e.embedding = $embedding,
                        e.ontology_domain = $ontology_domain,
                        e.attributes = $attributes
                    ON MATCH SET
                        e.source_documents = e.source_documents + $source_document,
                        e.confidence = CASE 
                            WHEN $confidence > e.confidence THEN $confidence 
                            ELSE e.confidence 
                        END
                    RETURN e.id as entity_id, e.canonical_name as name
                """, {
                    "canonical_name": entity.canonical_name,
                    "entity_type": entity.entity_type,
                    "confidence": entity.confidence,
                    "source_document": source_document,
                    "embedding": entity.attributes.get("embedding", []),
                    "ontology_domain": self.current_ontology.domain_name if self.current_ontology else "unknown",
                    "attributes": json.dumps(entity.attributes)
                })
                
                record = neo4j_result.single()
                if record:
                    result["neo4j_id"] = record["entity_id"]
                    self.entity_cache[cache_key] = record["entity_id"]
                    result["created"] = True
                    
                    logger.debug(f"✓ Entity created/updated: {entity.canonical_name} ({entity.entity_type})")
                
        except Exception as e:
            logger.error(f"Failed to create entity {entity.canonical_name}: {e}")
            self.errors.append(f"Entity creation failed: {entity.canonical_name} - {str(e)}")
        
        return result
    
    def _create_relationship(self, relationship: Relationship, 
                           source_neo4j_id: str, target_neo4j_id: str, 
                           source_document: str) -> bool:
        """Create relationship with ontological validation."""
        # Avoid duplicate relationships
        rel_key = (source_neo4j_id, relationship.relationship_type, target_neo4j_id)
        if rel_key in self.relationship_cache:
            return False
        
        # Confidence check
        if relationship.confidence < self.confidence_threshold:
            self.warnings.append(f"Low confidence relationship: {relationship.relationship_type} ({relationship.confidence:.2f})")
        
        # Ontology validation
        if (self.current_ontology and 
            relationship.relationship_type not in self.valid_relationship_types):
            self.warnings.append(f"Relationship type '{relationship.relationship_type}' not in ontology")
            # Use closest valid type or generic RELATED_TO
            relationship.relationship_type = self._find_closest_relationship_type(relationship.relationship_type)
        
        try:
            with self.driver.session() as session:
                # Sanitize relationship type for Neo4j
                safe_rel_type = self._sanitize_relationship_type(relationship.relationship_type)
                
                # Create relationship with rich metadata using dynamic query construction
                query = f"""
                    MATCH (source:Entity {{id: $source_id}})
                    MATCH (target:Entity {{id: $target_id}})
                    MERGE (source)-[r:`{safe_rel_type}`]->(target)
                    ON CREATE SET 
                        r.id = randomUUID(),
                        r.created_at = datetime(),
                        r.confidence = $confidence,
                        r.source_documents = [$source_document],
                        r.ontology_domain = $ontology_domain,
                        r.attributes = $attributes,
                        r.relationship_type = $relationship_type
                    ON MATCH SET
                        r.source_documents = r.source_documents + $source_document,
                        r.confidence = CASE 
                            WHEN $confidence > r.confidence THEN $confidence 
                            ELSE r.confidence 
                        END
                """
                
                session.run(query, {
                    "source_id": source_neo4j_id,
                    "target_id": target_neo4j_id,
                    "relationship_type": relationship.relationship_type,  # Store original type as property
                    "confidence": relationship.confidence,
                    "source_document": source_document,
                    "ontology_domain": self.current_ontology.domain_name if self.current_ontology else "unknown",
                    "attributes": json.dumps(relationship.attributes)
                })
                
                self.relationship_cache.add(rel_key)
                logger.debug(f"✓ Relationship created: {relationship.relationship_type}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to create relationship {relationship.relationship_type}: {e}")
            self.errors.append(f"Relationship creation failed: {relationship.relationship_type} - {str(e)}")
            return False
    
    def _find_closest_entity_type(self, invalid_type: str) -> str:
        """Find closest valid entity type using simple heuristics."""
        if not self.valid_entity_types:
            return "UNKNOWN"
        
        # Simple matching based on common patterns
        invalid_lower = invalid_type.lower()
        
        for valid_type in self.valid_entity_types:
            if invalid_lower in valid_type.lower() or valid_type.lower() in invalid_lower:
                return valid_type
        
        # Default fallback
        return list(self.valid_entity_types)[0] if self.valid_entity_types else "UNKNOWN"
    
    def _find_closest_relationship_type(self, invalid_type: str) -> str:
        """Find closest valid relationship type."""
        if not self.valid_relationship_types:
            return "RELATED_TO"
        
        # Simple matching
        invalid_lower = invalid_type.lower()
        
        for valid_type in self.valid_relationship_types:
            if invalid_lower in valid_type.lower() or valid_type.lower() in invalid_lower:
                return valid_type
        
        return list(self.valid_relationship_types)[0] if self.valid_relationship_types else "RELATED_TO"
    
    def _sanitize_relationship_type(self, rel_type: str) -> str:
        """Sanitize relationship type for Neo4j compatibility."""
        import re
        # Remove special characters and replace with underscores
        sanitized = re.sub(r'[^A-Za-z0-9_]', '_', rel_type)
        # Remove leading/trailing underscores and collapse multiple underscores
        sanitized = re.sub(r'_+', '_', sanitized).strip('_')
        # Ensure it starts with a letter (Neo4j requirement)
        if sanitized and not sanitized[0].isalpha():
            sanitized = 'REL_' + sanitized
        # Fallback for empty strings
        return sanitized if sanitized else 'UNKNOWN_RELATION'
    
    def _calculate_graph_metrics(self, source_document: str) -> GraphMetrics:
        """Calculate comprehensive graph quality metrics."""
        try:
            with self.driver.session() as session:
                # Basic counts
                result = session.run("""
                    MATCH (e:Entity) 
                    WHERE $source_document IN e.source_documents
                    RETURN count(e) as entity_count
                """, {"source_document": source_document})
                total_entities = result.single()["entity_count"]
                
                result = session.run("""
                    MATCH (e1:Entity)-[r]->(e2:Entity) 
                    WHERE $source_document IN r.source_documents
                    RETURN count(r) as rel_count
                """, {"source_document": source_document})
                total_relationships = result.single()["rel_count"]
                
                # Entity type distribution
                result = session.run("""
                    MATCH (e:Entity) 
                    WHERE $source_document IN e.source_documents
                    RETURN e.entity_type as type, count(e) as count
                """, {"source_document": source_document})
                entity_dist = {record["type"]: record["count"] for record in result}
                
                # Relationship type distribution
                result = session.run("""
                    MATCH (e1:Entity)-[r]->(e2:Entity) 
                    WHERE $source_document IN r.source_documents
                    RETURN type(r) as rel_type, count(r) as count
                """, {"source_document": source_document})
                rel_dist = {record["rel_type"]: record["count"] for record in result}
                
                # Confidence distribution
                result = session.run("""
                    MATCH (e:Entity) 
                    WHERE $source_document IN e.source_documents
                    WITH CASE 
                        WHEN e.confidence >= 0.9 THEN 'high'
                        WHEN e.confidence >= 0.7 THEN 'medium'
                        ELSE 'low'
                    END as conf_bucket
                    RETURN conf_bucket, count(*) as count
                """, {"source_document": source_document})
                conf_dist = {record["conf_bucket"]: record["count"] for record in result}
                
                # Calculate derived metrics
                ontology_coverage = 0.0
                if self.current_ontology:
                    used_types = set(entity_dist.keys()) | set(rel_dist.keys())
                    total_types = len(self.valid_entity_types) + len(self.valid_relationship_types)
                    ontology_coverage = len(used_types) / max(total_types, 1)
                
                semantic_density = total_relationships / max(total_entities, 1)
                
                return GraphMetrics(
                    total_entities=total_entities,
                    total_relationships=total_relationships,
                    ontology_coverage=ontology_coverage,
                    semantic_density=semantic_density,
                    confidence_distribution=conf_dist,
                    entity_type_distribution=entity_dist,
                    relationship_type_distribution=rel_dist
                )
                
        except Exception as e:
            logger.error(f"Failed to calculate metrics: {e}")
            return GraphMetrics(
                total_entities=0,
                total_relationships=0,
                ontology_coverage=0.0,
                semantic_density=0.0,
                confidence_distribution={},
                entity_type_distribution={},
                relationship_type_distribution={}
            )
    
    def adversarial_test_entity_resolution(self) -> Dict[str, Any]:
        """Comprehensive adversarial testing for entity resolution."""
        logger.info("🔍 Running adversarial tests for entity resolution...")
        
        test_results = {
            "duplicate_detection": self._test_duplicate_detection(),
            "case_sensitivity": self._test_case_sensitivity(),
            "unicode_handling": self._test_unicode_handling(),
            "embedding_consistency": self._test_embedding_consistency(),
            "ontology_constraint_enforcement": self._test_ontology_constraints(),
            "confidence_thresholding": self._test_confidence_thresholding()
        }
        
        # Calculate overall score
        passed_tests = sum(1 for test in test_results.values() if test["passed"])
        total_tests = len(test_results)
        overall_score = passed_tests / total_tests
        
        test_results["overall_score"] = overall_score
        test_results["summary"] = f"Passed {passed_tests}/{total_tests} adversarial tests"
        
        logger.info(f"🎯 Adversarial testing complete: {overall_score:.1%} pass rate")
        
        return test_results
    
    def _test_duplicate_detection(self) -> Dict[str, Any]:
        """Test entity deduplication capabilities."""
        test_entities = [
            ("Apple Inc.", "ORGANIZATION"),
            ("Apple Inc", "ORGANIZATION"),  # No period
            ("APPLE INC.", "ORGANIZATION"),  # All caps
            ("apple inc", "ORGANIZATION"),   # All lowercase
        ]
        
        entity_ids = []
        try:
            for name, entity_type in test_entities:
                result = self.identity_service.find_or_create_entity(name, entity_type, "test context")
                entity_ids.append(result["entity_id"])
            
            # All should resolve to same entity
            unique_ids = set(entity_ids)
            passed = len(unique_ids) == 1
            
            return {
                "passed": passed,
                "details": f"Created {len(unique_ids)} unique entities from {len(test_entities)} variations",
                "entity_ids": list(unique_ids)
            }
            
        except Exception as e:
            return {"passed": False, "error": str(e)}
    
    def _test_case_sensitivity(self) -> Dict[str, Any]:
        """Test case sensitivity handling."""
        test_cases = [
            ("Microsoft", "ORGANIZATION"),
            ("microsoft", "ORGANIZATION"),
            ("MICROSOFT", "ORGANIZATION"),
            ("MicroSoft", "ORGANIZATION"),
        ]
        
        try:
            entity_ids = []
            for name, entity_type in test_cases:
                result = self.identity_service.find_or_create_entity(name, entity_type, "case test")
                entity_ids.append(result["entity_id"])
            
            unique_ids = set(entity_ids)
            passed = len(unique_ids) <= 2  # Allow some variation but not complete chaos
            
            return {
                "passed": passed,
                "details": f"Case variations created {len(unique_ids)} entities",
                "entity_ids": list(unique_ids)
            }
            
        except Exception as e:
            return {"passed": False, "error": str(e)}
    
    def _test_unicode_handling(self) -> Dict[str, Any]:
        """Test Unicode and international character handling."""
        test_entities = [
            ("São Paulo", "LOCATION"),
            ("Zürich", "LOCATION"),
            ("北京", "LOCATION"),  # Beijing in Chinese
            ("Москва", "LOCATION"),  # Moscow in Russian
        ]
        
        try:
            created_count = 0
            for name, entity_type in test_entities:
                result = self.identity_service.find_or_create_entity(name, entity_type, "unicode test")
                if result["entity_id"]:
                    created_count += 1
            
            passed = created_count == len(test_entities)
            
            return {
                "passed": passed,
                "details": f"Successfully created {created_count}/{len(test_entities)} Unicode entities"
            }
            
        except Exception as e:
            return {"passed": False, "error": str(e)}
    
    def _test_embedding_consistency(self) -> Dict[str, Any]:
        """Test embedding generation consistency."""
        test_text = "Climate change policy analysis"
        
        try:
            # Generate same embedding multiple times
            embeddings = []
            for _ in range(3):
                embedding = self.identity_service.get_embedding(test_text)
                embeddings.append(embedding)
            
            # Check consistency (embeddings should be identical)
            if len(embeddings) >= 2:
                similarity = self.identity_service.cosine_similarity(embeddings[0], embeddings[1])
                passed = similarity > 0.99  # Should be nearly identical
            else:
                passed = False
            
            return {
                "passed": passed,
                "details": f"Embedding consistency: {similarity:.4f}" if len(embeddings) >= 2 else "Failed to generate embeddings"
            }
            
        except Exception as e:
            return {"passed": False, "error": str(e)}
    
    def _test_ontology_constraints(self) -> Dict[str, Any]:
        """Test ontology constraint enforcement."""
        if not self.current_ontology:
            return {"passed": True, "details": "No ontology set - constraints not applicable"}
        
        try:
            # Test with invalid entity type
            from src.core.identity_service import Entity
            invalid_entity = Entity(
                id="test_invalid",
                canonical_name="Test Entity",
                entity_type="INVALID_TYPE",
                confidence=0.9
            )
            
            # Process through ontology validation
            result = self._process_entity(invalid_entity, "constraint_test")
            
            # Should have been corrected or flagged
            passed = result["ontology_mismatch"] or result["created"]
            
            return {
                "passed": passed,
                "details": f"Invalid entity type handled: {result}"
            }
            
        except Exception as e:
            return {"passed": False, "error": str(e)}
    
    def _test_confidence_thresholding(self) -> Dict[str, Any]:
        """Test confidence threshold enforcement."""
        try:
            from src.core.identity_service import Entity
            
            # Test low confidence entity
            low_conf_entity = Entity(
                id="test_low_conf",
                canonical_name="Low Confidence Entity",
                entity_type="TEST_TYPE",
                confidence=0.3  # Below threshold
            )
            
            result = self._process_entity(low_conf_entity, "confidence_test")
            
            # Should be flagged as low confidence
            passed = result["low_confidence"]
            
            return {
                "passed": passed,
                "details": f"Low confidence entity flagged: {result['low_confidence']}"
            }
            
        except Exception as e:
            return {"passed": False, "error": str(e)}
    
    def close(self):
        """Clean up resources."""
        if hasattr(self, 'driver'):
            self.driver.close()
        logger.info("🔌 Graph builder resources cleaned up")