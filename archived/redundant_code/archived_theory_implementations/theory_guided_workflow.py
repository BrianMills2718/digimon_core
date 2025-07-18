"""
Theory-Guided Workflow for Phase 1

This module implements true theory-aware processing that uses theory schemas
to guide extraction during the process, not just validate afterward.

Addresses CLAUDE.md Task P2.1: Replace Post-Processing Validation with Theory-Guided Processing
"""

import time
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from ...core.config_manager import ConfigManager
from ...core.logging_config import get_logger
from ..phase1.t01_pdf_loader import PDFLoader
from ..phase1.t15a_text_chunker import TextChunker
from ..phase1.t23a_spacy_ner import SpacyNER
from ..phase1.t27_relationship_extractor import RelationshipExtractor
from ..phase1.t31_entity_builder import EntityBuilder
from ..phase1.t34_edge_builder import EdgeBuilder


@dataclass
class TheoryGuidedResult:
    """Result of theory-guided processing"""
    entities: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]
    graph: Dict[str, Any]
    theory_alignment_score: float
    concept_usage: Dict[str, int]
    theory_metadata: Dict[str, Any]


class TheoryGuidedWorkflow:
    """Workflow that uses theory to GUIDE extraction, not just validate"""
    
    def __init__(self, config_manager: ConfigManager, theory_schema):
        self.config_manager = config_manager
        self.theory_schema = theory_schema
        self.concept_library = self._load_concept_library()
        self.logger = get_logger("theory_guided_workflow")
        
        # Initialize services
        self.identity_service = self._create_identity_service()
        self.provenance_service = self._create_provenance_service()
        self.quality_service = self._create_quality_service()
        
        # Initialize tools
        self._initialize_tools()
    
    def _create_identity_service(self):
        """Create identity service"""
        try:
            from ...core.identity_service import IdentityService
            return IdentityService()
        except ImportError:
            return None
    
    def _create_provenance_service(self):
        """Create provenance service"""
        try:
            from ...core.provenance_service import ProvenanceService
            return ProvenanceService()
        except ImportError:
            return None
    
    def _create_quality_service(self):
        """Create quality service"""
        try:
            from ...core.quality_service import QualityService
            return QualityService()
        except ImportError:
            return None
    
    def _initialize_tools(self):
        """Initialize processing tools with theory guidance"""
        # Get Neo4j config
        neo4j_config = self.config_manager.get_neo4j_config()
        
        # Initialize tools
        self.pdf_loader = PDFLoader(
            self.identity_service, 
            self.provenance_service, 
            self.quality_service
        )
        
        self.text_chunker = TextChunker(
            self.identity_service, 
            self.provenance_service, 
            self.quality_service
        )
        
        self.spacy_ner = SpacyNER(
            self.identity_service, 
            self.provenance_service, 
            self.quality_service
        )
        
        self.relationship_extractor = RelationshipExtractor(
            self.identity_service, 
            self.provenance_service, 
            self.quality_service
        )
        
        self.entity_builder = EntityBuilder(
            self.identity_service, 
            self.provenance_service, 
            self.quality_service,
            neo4j_config['uri'], 
            neo4j_config['user'], 
            neo4j_config['password']
        )
        
        self.edge_builder = EdgeBuilder(
            self.identity_service, 
            self.provenance_service, 
            self.quality_service,
            neo4j_config['uri'], 
            neo4j_config['user'], 
            neo4j_config['password']
        )
    
    def _load_concept_library(self):
        """Load concept library from theory schema"""
        try:
            if hasattr(self.theory_schema, 'concept_library_path'):
                # Try to load from file path
                import importlib.util
                spec = importlib.util.spec_from_file_location(
                    "concept_library", 
                    self.theory_schema.concept_library_path
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Try different possible structures
                if hasattr(module, 'MASTER_CONCEPTS'):
                    return getattr(module, 'MASTER_CONCEPTS')
                elif hasattr(module, 'MasterConceptRegistry'):
                    # Try to create a registry and extract concepts
                    registry_class = getattr(module, 'MasterConceptRegistry')
                    registry = registry_class()
                    return self._convert_registry_to_dict(registry)
                else:
                    self.logger.warning("Concept library file found but no recognized structure")
                    return self._get_default_concept_library()
            else:
                # Use default concept library
                return self._get_default_concept_library()
        except Exception as e:
            self.logger.warning(f"Failed to load concept library: {e}, using defaults")
            return self._get_default_concept_library()
    
    def _convert_registry_to_dict(self, registry):
        """Convert MasterConceptRegistry to simple dictionary format"""
        try:
            concept_dict = {}
            
            # Convert entities
            for name, entity in registry.entities.items():
                concept_dict[name.upper()] = {
                    "description": entity.description,
                    "patterns": entity.indigenous_term + entity.aliases,
                    "relationships": []  # Will be populated from connections
                }
            
            # Add connections as relationships
            for name, connection in registry.connections.items():
                domain = getattr(connection, 'domain', [])
                range_types = getattr(connection, 'range', [])
                
                for domain_type in domain:
                    if domain_type.upper() in concept_dict:
                        concept_dict[domain_type.upper()]["relationships"].append(name)
            
            return concept_dict if concept_dict else self._get_default_concept_library()
            
        except Exception as e:
            self.logger.warning(f"Failed to convert registry to dict: {e}")
            return self._get_default_concept_library()
    
    def _get_default_concept_library(self):
        """Default concept library for theory guidance"""
        return {
            "PERSON": {
                "description": "Individual human beings",
                "patterns": ["person", "individual", "people", "human"],
                "relationships": ["works_at", "lives_in", "leads", "founded"]
            },
            "ORGANIZATION": {
                "description": "Companies, institutions, groups",
                "patterns": ["company", "organization", "institution", "corp", "inc"],
                "relationships": ["located_in", "owns", "partners_with", "competes_with"]
            },
            "LOCATION": {
                "description": "Geographic places and locations",
                "patterns": ["city", "country", "state", "region", "place"],
                "relationships": ["contains", "borders", "near"]
            },
            "PRODUCT": {
                "description": "Products, services, technologies",
                "patterns": ["product", "service", "technology", "solution"],
                "relationships": ["produced_by", "used_by", "competes_with"]
            }
        }
    
    def execute_with_theory_guidance(self, document_paths, queries, theory_schema, concept_library):
        """Execute workflow with theory guiding each step"""
        start_time = time.time()
        
        try:
            self.logger.info("🧠 Starting theory-guided processing with %d concepts", 
                           len(concept_library))
            
            # 1. Load documents
            documents = self._load_documents(document_paths)
            
            # 2. Theory-guided chunking (use concepts to inform chunk boundaries)
            chunks = self._theory_guided_chunking(documents, concept_library)
            
            # 3. Theory-guided NER (prioritize entity types from concept library)
            entities = self._theory_guided_ner(chunks, concept_library)
            
            # 4. Theory-guided relationship extraction (use concept relationships)
            relationships = self._theory_guided_relationships(entities, concept_library)
            
            # 5. Theory-guided graph construction
            graph = self._build_theory_aligned_graph(entities, relationships, concept_library)
            
            # 6. Calculate theory alignment score
            alignment_score = self._calculate_alignment_score(graph, theory_schema)
            
            # 7. Generate concept usage statistics
            concept_usage = self._calculate_concept_usage(entities, concept_library)
            
            theory_metadata = {
                "processing_time": time.time() - start_time,
                "theory_schema_type": str(theory_schema.schema_type) if hasattr(theory_schema, 'schema_type') else "unknown",
                "concepts_available": len(concept_library),
                "concepts_used": len([k for k, v in concept_usage.items() if v > 0])
            }
            
            self.logger.info("✅ Theory-guided processing complete: %d entities, %d relationships, alignment: %.2f", 
                           len(entities), len(relationships), alignment_score)
            
            return TheoryGuidedResult(
                entities=entities,
                relationships=relationships,
                graph=graph,
                theory_alignment_score=alignment_score,
                concept_usage=concept_usage,
                theory_metadata=theory_metadata
            )
            
        except Exception as e:
            self.logger.error("❌ Theory-guided processing failed: %s", str(e), exc_info=True)
            raise
    
    def _load_documents(self, document_paths):
        """Load documents from paths"""
        documents = []
        for path in document_paths:
            try:
                result = self.pdf_loader.load_pdf(path)
                if result.get("status") == "success":
                    documents.append(result.get("document", {}))
            except Exception as e:
                self.logger.warning(f"Failed to load document {path}: {e}")
        return documents
    
    def _theory_guided_chunking(self, documents, concept_library):
        """Use concept boundaries to inform chunking strategy"""
        self.logger.info("🔍 Theory-guided chunking with concept awareness")
        
        all_chunks = []
        
        for doc in documents:
            text = doc.get("text", "")
            doc_id = doc.get("document_id", "unknown")
            
            if not text:
                continue
                
            try:
                # Standard chunking first
                result = self.text_chunker.chunk_text(doc_id, text, 0.8)
                
                if result.get("status") == "success":
                    chunks = result.get("chunks", [])
                    
                    # Apply theory guidance to chunking
                    enhanced_chunks = []
                    for chunk in chunks:
                        chunk_text = chunk.get("text", "")
                        
                        # Analyze chunk for concept density
                        concept_density = self._calculate_concept_density(chunk_text, concept_library)
                        
                        # Enhance chunk metadata with theory information
                        chunk["theory_metadata"] = {
                            "concept_density": concept_density,
                            "dominant_concepts": self._find_dominant_concepts(chunk_text, concept_library),
                            "theory_relevance": concept_density / len(concept_library) if concept_library else 0.0
                        }
                        
                        enhanced_chunks.append(chunk)
                    
                    all_chunks.extend(enhanced_chunks)
                    
            except Exception as e:
                self.logger.warning(f"Theory-guided chunking failed for document {doc_id}: {e}")
        
        self.logger.info("📄 Created %d theory-aware chunks", len(all_chunks))
        return all_chunks
    
    def _theory_guided_ner(self, chunks, concept_library):
        """Prioritize entity recognition based on concept library"""
        self.logger.info("🏷️  Theory-guided NER with concept prioritization")
        
        all_entities = []
        
        for chunk in chunks:
            chunk_id = chunk.get("chunk_id", "unknown")
            text = chunk.get("text", "")
            
            if not text:
                continue
                
            try:
                # Standard NER first
                result = self.spacy_ner.extract_entities(chunk_id, text, 0.8)
                
                if result.get("status") == "success":
                    entities = result.get("entities", [])
                    
                    # Apply theory guidance to entity extraction
                    enhanced_entities = []
                    for entity in entities:
                        surface_form = entity.get("surface_form", "")
                        entity_type = entity.get("entity_type", "")
                        
                        # Map to concept library
                        concept_match = self._find_best_concept_match(surface_form, entity_type, concept_library)
                        
                        # Enhance entity with theory information
                        if concept_match:
                            entity["theory_metadata"] = {
                                "concept_match": concept_match["concept"],
                                "concept_confidence": concept_match["confidence"],
                                "theory_enhanced": True,
                                "concept_description": concept_match.get("description", "")
                            }
                            
                            # Boost confidence for theory-aligned entities
                            entity["confidence"] = min(1.0, entity.get("confidence", 0.0) + 0.1)
                        else:
                            entity["theory_metadata"] = {
                                "concept_match": None,
                                "concept_confidence": 0.0,
                                "theory_enhanced": False
                            }
                        
                        enhanced_entities.append(entity)
                    
                    all_entities.extend(enhanced_entities)
                    
            except Exception as e:
                self.logger.warning(f"Theory-guided NER failed for chunk {chunk_id}: {e}")
        
        self.logger.info("🏷️  Extracted %d theory-aware entities", len(all_entities))
        return all_entities
    
    def _theory_guided_relationships(self, entities, concept_library):
        """Extract relationships using concept library relationship patterns"""
        self.logger.info("🔗 Theory-guided relationship extraction")
        
        # Group entities by chunk for relationship extraction
        chunk_entities = {}
        for entity in entities:
            chunk_id = entity.get("source_chunk", "unknown")
            if chunk_id not in chunk_entities:
                chunk_entities[chunk_id] = []
            chunk_entities[chunk_id].append(entity)
        
        all_relationships = []
        
        for chunk_id, chunk_entity_list in chunk_entities.items():
            if len(chunk_entity_list) < 2:
                continue
                
            try:
                # Standard relationship extraction
                result = self.relationship_extractor.extract_relationships(
                    chunk_id, "", chunk_entity_list, 0.8
                )
                
                if result.get("status") == "success":
                    relationships = result.get("relationships", [])
                    
                    # Apply theory guidance to relationships
                    enhanced_relationships = []
                    for rel in relationships:
                        # Find subject and object entities
                        subject_entity = self._find_entity_by_id(rel.get("subject_entity_id"), entities)
                        object_entity = self._find_entity_by_id(rel.get("object_entity_id"), entities)
                        
                        if subject_entity and object_entity:
                            # Check if relationship aligns with concept library patterns
                            alignment_score = self._calculate_relationship_alignment(
                                subject_entity, object_entity, rel, concept_library
                            )
                            
                            rel["theory_metadata"] = {
                                "concept_alignment": alignment_score,
                                "theory_enhanced": alignment_score > 0.5,
                                "predicted_by_theory": alignment_score > 0.7
                            }
                            
                            # Boost confidence for theory-aligned relationships
                            if alignment_score > 0.5:
                                rel["confidence"] = min(1.0, rel.get("confidence", 0.0) + 0.1)
                        
                        enhanced_relationships.append(rel)
                    
                    all_relationships.extend(enhanced_relationships)
                    
            except Exception as e:
                self.logger.warning(f"Theory-guided relationship extraction failed for chunk {chunk_id}: {e}")
        
        self.logger.info("🔗 Extracted %d theory-aware relationships", len(all_relationships))
        return all_relationships
    
    def _build_theory_aligned_graph(self, entities, relationships, concept_library):
        """Build graph with theory alignment"""
        self.logger.info("🕸️  Building theory-aligned graph")
        
        try:
            # Build entities in Neo4j
            entity_mentions = []
            for entity in entities:
                mention = {
                    "mention_id": entity.get("mention_id", entity.get("entity_id", "")),
                    "entity_id": entity.get("entity_id", ""),
                    "surface_form": entity.get("surface_form", ""),
                    "canonical_name": entity.get("canonical_name", entity.get("surface_form", "")),
                    "entity_type": entity.get("entity_type", ""),
                    "confidence": entity.get("confidence", 0.0),
                    "theory_metadata": entity.get("theory_metadata", {})
                }
                entity_mentions.append(mention)
            
            entity_result = self.entity_builder.build_entities(entity_mentions, [])
            
            # Build relationships in Neo4j
            relationship_result = self.edge_builder.build_edges(relationships, [])
            
            # Create graph summary with theory information
            graph = {
                "entities_created": len(entities),
                "relationships_created": len(relationships),
                "theory_enhanced_entities": len([e for e in entities if e.get("theory_metadata", {}).get("theory_enhanced", False)]),
                "theory_enhanced_relationships": len([r for r in relationships if r.get("theory_metadata", {}).get("theory_enhanced", False)]),
                "concept_coverage": self._calculate_concept_coverage(entities, concept_library),
                "entity_build_status": entity_result.get("status", "unknown"),
                "relationship_build_status": relationship_result.get("status", "unknown")
            }
            
            return graph
            
        except Exception as e:
            self.logger.error(f"Theory-aligned graph building failed: {e}")
            return {
                "entities_created": len(entities),
                "relationships_created": len(relationships),
                "error": str(e)
            }
    
    def _calculate_alignment_score(self, graph, theory_schema):
        """Calculate how well the extracted graph aligns with theory"""
        try:
            total_entities = graph.get("entities_created", 0)
            theory_enhanced_entities = graph.get("theory_enhanced_entities", 0)
            
            total_relationships = graph.get("relationships_created", 0)
            theory_enhanced_relationships = graph.get("theory_enhanced_relationships", 0)
            
            if total_entities == 0 and total_relationships == 0:
                return 0.0
            
            # Calculate alignment as proportion of theory-enhanced elements
            entity_alignment = theory_enhanced_entities / total_entities if total_entities > 0 else 0.0
            relationship_alignment = theory_enhanced_relationships / total_relationships if total_relationships > 0 else 0.0
            
            # Weight entities and relationships equally
            overall_alignment = (entity_alignment + relationship_alignment) / 2
            
            return overall_alignment
            
        except Exception as e:
            self.logger.warning(f"Failed to calculate alignment score: {e}")
            return 0.0
    
    def _calculate_concept_usage(self, entities, concept_library):
        """Calculate how many times each concept was used"""
        usage = {concept: 0 for concept in concept_library.keys()}
        
        for entity in entities:
            concept_match = entity.get("theory_metadata", {}).get("concept_match")
            if concept_match and concept_match in usage:
                usage[concept_match] += 1
        
        return usage
    
    def _calculate_concept_density(self, text, concept_library):
        """Calculate how many concepts are mentioned in text"""
        density = 0
        text_lower = text.lower()
        
        for concept, info in concept_library.items():
            patterns = info.get("patterns", [])
            for pattern in patterns:
                if pattern.lower() in text_lower:
                    density += 1
                    break  # Count each concept only once per text
        
        return density
    
    def _find_dominant_concepts(self, text, concept_library):
        """Find the most relevant concepts in text"""
        matches = []
        text_lower = text.lower()
        
        for concept, info in concept_library.items():
            patterns = info.get("patterns", [])
            match_count = 0
            for pattern in patterns:
                match_count += text_lower.count(pattern.lower())
            
            if match_count > 0:
                matches.append({"concept": concept, "matches": match_count})
        
        # Sort by match count and return top 3
        matches.sort(key=lambda x: x["matches"], reverse=True)
        return [m["concept"] for m in matches[:3]]
    
    def _find_best_concept_match(self, surface_form, entity_type, concept_library):
        """Find the best concept match for an entity"""
        best_match = None
        best_score = 0.0
        
        surface_lower = surface_form.lower()
        type_lower = entity_type.lower()
        
        for concept, info in concept_library.items():
            score = 0.0
            
            # Check if entity type matches concept
            if concept.lower() in type_lower or type_lower in concept.lower():
                score += 0.5
            
            # Check pattern matches
            patterns = info.get("patterns", [])
            for pattern in patterns:
                if pattern.lower() in surface_lower:
                    score += 0.3
                    break
            
            # Check direct name match
            if concept.lower() in surface_lower:
                score += 0.2
            
            if score > best_score:
                best_score = score
                best_match = {
                    "concept": concept,
                    "confidence": score,
                    "description": info.get("description", "")
                }
        
        return best_match if best_score > 0.3 else None
    
    def _find_entity_by_id(self, entity_id, entities):
        """Find entity by ID in list"""
        for entity in entities:
            if entity.get("entity_id") == entity_id:
                return entity
        return None
    
    def _calculate_relationship_alignment(self, subject_entity, object_entity, relationship, concept_library):
        """Calculate how well a relationship aligns with concept library patterns"""
        score = 0.0
        
        # Get concept matches for entities
        subject_concept = subject_entity.get("theory_metadata", {}).get("concept_match")
        object_concept = object_entity.get("theory_metadata", {}).get("concept_match")
        
        if not subject_concept or not object_concept:
            return 0.0
        
        # Check if relationship type is expected between these concepts
        subject_info = concept_library.get(subject_concept, {})
        expected_relationships = subject_info.get("relationships", [])
        
        rel_type = relationship.get("relationship_type", "").lower()
        
        for expected_rel in expected_relationships:
            if expected_rel.lower() in rel_type or rel_type in expected_rel.lower():
                score += 0.8
                break
        
        # Bonus for high-confidence concept matches
        subject_conf = subject_entity.get("theory_metadata", {}).get("concept_confidence", 0.0)
        object_conf = object_entity.get("theory_metadata", {}).get("concept_confidence", 0.0)
        
        score += (subject_conf + object_conf) / 2 * 0.2
        
        return min(1.0, score)
    
    def _calculate_concept_coverage(self, entities, concept_library):
        """Calculate what percentage of concepts were used"""
        used_concepts = set()
        
        for entity in entities:
            concept_match = entity.get("theory_metadata", {}).get("concept_match")
            if concept_match:
                used_concepts.add(concept_match)
        
        total_concepts = len(concept_library)
        if total_concepts == 0:
            return 0.0
        
        return len(used_concepts) / total_concepts