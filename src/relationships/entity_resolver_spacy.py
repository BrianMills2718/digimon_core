"""
Entity Resolver using SpaCy NER for proper entity extraction and coreference resolution.

This module uses the existing T23A SpaCy NER tool instead of regex patterns
for much better accuracy in entity extraction and coreference resolution.
"""

import asyncio
import logging
import re
import numpy as np
from typing import List, Dict, Any, Set, Tuple, Optional
from dataclasses import dataclass, field
from collections import defaultdict
from difflib import SequenceMatcher
import spacy
from spacy.tokens import Doc

# Import the existing SpaCy NER tool
from src.tools.phase1.t23a_spacy_ner_unified import T23ASpacyNERUnified
from src.tools.base_tool import ToolRequest
from src.core.service_manager import ServiceManager

logger = logging.getLogger(__name__)


@dataclass
class EntityReference:
    """Reference to an entity across documents"""
    entity_id: str
    entity_name: str
    document_path: str
    mention_context: str
    confidence_score: float
    entity_type: str
    position_in_doc: int = 0
    aliases: List[str] = field(default_factory=list)


@dataclass
class EntityCluster:
    """Cluster of entity references that refer to the same entity"""
    cluster_id: str
    canonical_name: str
    entity_references: List[EntityReference]
    cluster_confidence: float
    entity_type: str
    disambiguation_confidence: float = 1.0


@dataclass
class EntityCoreferenceResult:
    """Result of entity coreference resolution"""
    entity_clusters: List[EntityCluster]
    resolution_statistics: Dict[str, Any]
    ambiguous_entities: List[str]


@dataclass
class EntityDisambiguationResult:
    """Result of entity disambiguation"""
    disambiguated_entities: List[EntityCluster]
    disambiguation_statistics: Dict[str, Any]
    confidence_scores: Dict[str, float]


class SpacyEntityResolver:
    """
    Resolves entity coreferences using SpaCy NER instead of regex patterns.
    """
    
    def __init__(self):
        self.logger = logger
        self.entity_cache = {}
        self.similarity_threshold = 0.6  # Can be lower with better entity extraction
        self.disambiguation_threshold = 0.7
        
        # Initialize SpaCy NER tool
        service_manager = ServiceManager()
        self.spacy_ner = T23ASpacyNERUnified(service_manager)
        
        # Load SpaCy model for additional processing
        try:
            self.nlp = spacy.load("en_core_web_sm")
            # Add coreference resolution if available
            try:
                import coreferee
                self.nlp.add_pipe('coreferee')
                self.has_coref = True
                logger.info("Coreferee coreference resolution enabled")
            except ImportError:
                self.has_coref = False
                logger.info("Coreferee not available, using basic coreference")
        except:
            logger.warning("SpaCy model not available, falling back to basic extraction")
            self.nlp = None
        
    async def resolve_entity_coreferences(self, documents: List[Dict[str, Any]]) -> EntityCoreferenceResult:
        """Link same entities across documents using SpaCy NER"""
        self.logger.info(f"Resolving entity coreferences in {len(documents)} documents using SpaCy")
        
        # Extract all entity mentions using SpaCy
        all_entity_refs = []
        for doc in documents:
            entity_refs = await self._extract_entity_references_spacy(doc)
            all_entity_refs.extend(entity_refs)
        
        # Cluster entities by similarity
        entity_clusters = self._cluster_entities_smart(all_entity_refs)
        
        # Calculate statistics
        resolution_stats = {
            "total_entity_mentions": len(all_entity_refs),
            "unique_entities": len(entity_clusters),
            "average_cluster_size": np.mean([len(cluster.entity_references) for cluster in entity_clusters]) if entity_clusters else 0,
            "coreference_links": sum(len(cluster.entity_references) - 1 for cluster in entity_clusters if len(cluster.entity_references) > 1)
        }
        
        # Identify ambiguous entities
        ambiguous_entities = []
        for cluster in entity_clusters:
            if cluster.cluster_confidence < 0.7 or len(set(ref.entity_type for ref in cluster.entity_references)) > 1:
                ambiguous_entities.append(cluster.canonical_name)
        
        return EntityCoreferenceResult(
            entity_clusters=entity_clusters,
            resolution_statistics=resolution_stats,
            ambiguous_entities=ambiguous_entities
        )
    
    async def _extract_entity_references_spacy(self, document: Dict[str, Any]) -> List[EntityReference]:
        """Extract entity references using SpaCy NER tool"""
        content = document.get("content", "")
        doc_path = document.get("path", "")
        metadata = document.get("metadata", {})
        
        entity_refs = []
        
        # Use the SpaCy NER tool for extraction
        tool_request = ToolRequest(
            tool_id="T23A_ENHANCED",
            operation="extract",
            input_data={
                "text": content,
                "chunk_ref": doc_path
            },
            parameters={
                "confidence_threshold": 0.3,  # Lowered from 0.7 to capture more entities
                "entity_types": ["PERSON", "ORG", "GPE", "LOC", "EVENT", "FAC"]
            }
        )
        
        # Execute SpaCy NER extraction
        result = self.spacy_ner.execute(tool_request)
        
        if result.status == "success":
            entities = result.data.get("entities", [])
            
            for entity in entities:
                # Create entity reference from SpaCy extraction
                entity_ref = EntityReference(
                    entity_id=f"{doc_path}_{entity['entity_id']}",
                    entity_name=entity['surface_form'],
                    document_path=doc_path,
                    mention_context=self._get_context(content, entity['start_pos'], entity['end_pos']),
                    confidence_score=entity['confidence'],
                    entity_type=entity['entity_type'],
                    position_in_doc=entity['start_pos'],
                    aliases=self._generate_aliases(entity['surface_form'])
                )
                entity_refs.append(entity_ref)
        
        # If SpaCy model is available, also do coreference resolution
        if self.nlp and self.has_coref and content:
            doc = self.nlp(content)
            
            # Process coreference chains if available
            if hasattr(doc._, 'coref_chains'):
                for chain in doc._.coref_chains:
                    # Get the main mention
                    main_mention = chain.most_specific_mention_text
                    
                    # Add all coreferent mentions
                    for mention in chain.mentions:
                        if mention.text != main_mention:
                            # This is a pronoun or alternative reference
                            entity_ref = EntityReference(
                                entity_id=f"{doc_path}_coref_{len(entity_refs)}",
                                entity_name=main_mention,  # Resolve to main mention
                                document_path=doc_path,
                                mention_context=self._get_context(content, mention.start_char, mention.end_char),
                                confidence_score=0.9,  # High confidence from coref model
                                entity_type="PERSON" if self._is_person_pronoun(mention.text) else "ENTITY",
                                position_in_doc=mention.start_char,
                                aliases=[mention.text]  # Store the actual pronoun/reference
                            )
                            entity_refs.append(entity_ref)
        
        # Skip metadata extraction for now - it's adding non-entity values like "Science Writer"
        # TODO: Add proper validation to ensure metadata contains real entity names
        
        return entity_refs
    
    def _get_context(self, text: str, start_pos: int, end_pos: int, window: int = 50) -> str:
        """Get context around an entity mention"""
        context_start = max(0, start_pos - window)
        context_end = min(len(text), end_pos + window)
        return text[context_start:context_end].strip()
    
    def _is_person_pronoun(self, text: str) -> bool:
        """Check if text is a person pronoun"""
        person_pronouns = {"he", "she", "him", "her", "his", "hers", "they", "them", "their"}
        return text.lower() in person_pronouns
    
    def _cluster_entities_smart(self, entity_refs: List[EntityReference]) -> List[EntityCluster]:
        """Cluster entities using smarter similarity metrics"""
        clusters = []
        
        # Group entities by type first for efficiency
        entities_by_type = defaultdict(list)
        for ref in entity_refs:
            entities_by_type[ref.entity_type].append(ref)
        
        # Cluster within each type
        for entity_type, refs in entities_by_type.items():
            type_clusters = self._cluster_entities_by_type_smart(refs, entity_type)
            clusters.extend(type_clusters)
        
        return clusters
    
    def _cluster_entities_by_type_smart(self, entity_refs: List[EntityReference], entity_type: str) -> List[EntityCluster]:
        """Cluster entities of the same type using better similarity"""
        if not entity_refs:
            return []
        
        clusters = []
        unassigned_refs = entity_refs.copy()
        
        while unassigned_refs:
            # Start new cluster with first unassigned reference
            seed_ref = unassigned_refs.pop(0)
            cluster_refs = [seed_ref]
            
            # Find similar references
            to_remove = []
            for i, ref in enumerate(unassigned_refs):
                similarity = self._calculate_entity_similarity_smart(seed_ref, ref)
                if similarity > self.similarity_threshold:
                    cluster_refs.append(ref)
                    to_remove.append(i)
            
            # Remove assigned references
            for i in reversed(to_remove):
                unassigned_refs.pop(i)
            
            # Create cluster
            canonical_name = self._select_canonical_name(cluster_refs)
            cluster_confidence = self._calculate_cluster_confidence(cluster_refs)
            
            cluster = EntityCluster(
                cluster_id=f"cluster_{entity_type}_{len(clusters)}",
                canonical_name=canonical_name,
                entity_references=cluster_refs,
                cluster_confidence=cluster_confidence,
                entity_type=entity_type
            )
            clusters.append(cluster)
        
        return clusters
    
    def _calculate_entity_similarity_smart(self, ref1: EntityReference, ref2: EntityReference) -> float:
        """Calculate similarity using better metrics"""
        name1_lower = ref1.entity_name.lower()
        name2_lower = ref2.entity_name.lower()
        
        # Exact match
        if name1_lower == name2_lower:
            return 1.0
        
        # Check if one is a substring of the other (e.g., "Chen" in "Sarah Chen")
        if name1_lower in name2_lower or name2_lower in name1_lower:
            return 0.9
        
        # Check for last name match for persons
        if ref1.entity_type == "PERSON" and ref2.entity_type == "PERSON":
            parts1 = name1_lower.split()
            parts2 = name2_lower.split()
            
            # Both have multiple parts - check last name
            if len(parts1) > 1 and len(parts2) > 1:
                if parts1[-1] == parts2[-1]:
                    # Same last name - check context
                    context_sim = self._calculate_context_similarity(ref1.mention_context, ref2.mention_context)
                    if context_sim > 0.3:
                        return 0.85  # Likely same person
                    else:
                        return 0.4   # Different people with same last name
            
            # One is just last name, other is full name
            if len(parts1) == 1 and len(parts2) > 1:
                if parts1[0] == parts2[-1]:
                    return 0.8
            elif len(parts2) == 1 and len(parts1) > 1:
                if parts2[0] == parts1[-1]:
                    return 0.8
        
        # Check aliases (including pronouns resolved by coref)
        for alias1 in [name1_lower] + [a.lower() for a in ref1.aliases]:
            for alias2 in [name2_lower] + [a.lower() for a in ref2.aliases]:
                if alias1 == alias2:
                    return 0.85
        
        # String similarity
        name_sim = SequenceMatcher(None, name1_lower, name2_lower).ratio()
        
        # Context similarity
        context_sim = self._calculate_context_similarity(ref1.mention_context, ref2.mention_context)
        
        # Weighted combination
        similarity = name_sim * 0.6 + context_sim * 0.4
        
        return similarity
    
    def _calculate_context_similarity(self, context1: str, context2: str) -> float:
        """Calculate similarity between entity contexts"""
        # Simple word overlap similarity
        words1 = set(re.findall(r'\b\w+\b', context1.lower()))
        words2 = set(re.findall(r'\b\w+\b', context2.lower()))
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _select_canonical_name(self, entity_refs: List[EntityReference]) -> str:
        """Select the canonical name for an entity cluster"""
        if not entity_refs:
            return ""
        
        # Prefer longer, more complete names with higher confidence
        names_with_scores = []
        for ref in entity_refs:
            # Prefer full names over partial names
            name_parts = ref.entity_name.split()
            completeness_score = len(name_parts) * 10
            
            # Prefer names from metadata (authors)
            metadata_bonus = 20 if "author" in ref.entity_id.lower() else 0
            
            score = completeness_score + ref.confidence_score * 10 + metadata_bonus
            names_with_scores.append((ref.entity_name, score))
        
        # Sort by score and return best name
        names_with_scores.sort(key=lambda x: x[1], reverse=True)
        return names_with_scores[0][0]
    
    def _calculate_cluster_confidence(self, entity_refs: List[EntityReference]) -> float:
        """Calculate confidence score for an entity cluster"""
        if not entity_refs:
            return 0.0
        
        # Base confidence on individual reference confidences
        avg_confidence = np.mean([ref.confidence_score for ref in entity_refs])
        
        # Boost confidence for clusters with multiple references
        size_boost = min(0.2, (len(entity_refs) - 1) * 0.05)
        
        # Boost for consistent entity types
        types = set(ref.entity_type for ref in entity_refs)
        type_consistency_boost = 0.1 if len(types) == 1 else 0.0
        
        cluster_confidence = avg_confidence + size_boost + type_consistency_boost
        return min(1.0, cluster_confidence)
    
    def _generate_aliases(self, entity_name: str) -> List[str]:
        """Generate possible aliases for an entity"""
        aliases = []
        
        # For person names
        parts = entity_name.split()
        if len(parts) >= 2:
            # Last name only
            aliases.append(parts[-1])
            
            # First name only
            aliases.append(parts[0])
            
            # Initials + Last name
            if len(parts[0]) > 0:
                aliases.append(f"{parts[0][0]}. {parts[-1]}")
            
            # With titles
            if not any(title in entity_name.lower() for title in ["dr.", "prof.", "mr.", "ms.", "mrs."]):
                aliases.extend([f"Dr. {entity_name}", f"Prof. {entity_name}"])
        
        return aliases
    
    async def disambiguate_entities(self, documents: List[Dict[str, Any]]) -> EntityDisambiguationResult:
        """Disambiguate entities with same names but different identities"""
        self.logger.info(f"Disambiguating entities in {len(documents)} documents")
        
        # First resolve coreferences
        coreference_result = await self.resolve_entity_coreferences(documents)
        
        # Find potentially ambiguous clusters (entities with same/similar names)
        name_groups = defaultdict(list)
        for cluster in coreference_result.entity_clusters:
            normalized_name = self._normalize_entity_name(cluster.canonical_name)
            name_groups[normalized_name].append(cluster)
        
        # Disambiguate clusters with same normalized names
        disambiguated_entities = []
        disambiguation_stats = {
            "ambiguous_name_groups": 0,
            "entities_disambiguated": 0,
            "disambiguation_accuracy": 0.0
        }
        confidence_scores = {}
        
        for normalized_name, clusters in name_groups.items():
            if len(clusters) > 1:
                # Multiple clusters with same normalized name - need disambiguation
                disambiguation_stats["ambiguous_name_groups"] += 1
                
                # Use context to disambiguate
                disambiguated = self._disambiguate_by_context(clusters)
                disambiguated_entities.extend(disambiguated)
                
                for cluster in disambiguated:
                    confidence_scores[cluster.cluster_id] = cluster.disambiguation_confidence
                    
                disambiguation_stats["entities_disambiguated"] += len(disambiguated)
            else:
                # Single cluster - no disambiguation needed
                cluster = clusters[0]
                cluster.disambiguation_confidence = 1.0
                disambiguated_entities.append(cluster)
                confidence_scores[cluster.cluster_id] = 1.0
        
        # Calculate overall disambiguation accuracy
        if confidence_scores:
            disambiguation_stats["disambiguation_accuracy"] = np.mean(list(confidence_scores.values()))
        
        return EntityDisambiguationResult(
            disambiguated_entities=disambiguated_entities,
            disambiguation_statistics=disambiguation_stats,
            confidence_scores=confidence_scores
        )
    
    def _normalize_entity_name(self, name: str) -> str:
        """Normalize entity name for grouping"""
        # Remove titles and normalize case
        normalized = re.sub(r'\b(?:Dr\.|Prof\.|Mr\.|Ms\.|Mrs\.)\s+', '', name)
        normalized = normalized.lower().strip()
        
        # Get last name for person entities
        parts = normalized.split()
        if len(parts) > 1:
            return parts[-1]  # Group by last name
        
        return normalized
    
    def _disambiguate_by_context(self, clusters: List[EntityCluster]) -> List[EntityCluster]:
        """Disambiguate clusters using context analysis"""
        # Analyze context keywords for each cluster
        for cluster in clusters:
            contexts = [ref.mention_context for ref in cluster.entity_references]
            combined_context = " ".join(contexts).lower()
            
            # Extract disambiguating features
            disambiguation_score = 0.5  # Base score
            
            # Check for specific domain indicators
            if "crispr" in combined_context or "gene" in combined_context:
                cluster.domain = "genetics"
                disambiguation_score += 0.2
            elif "cancer" in combined_context or "immunotherapy" in combined_context:
                cluster.domain = "oncology"
                disambiguation_score += 0.2
            
            # Check for institutional affiliations
            if "stanford" in combined_context:
                cluster.affiliation = "Stanford"
                disambiguation_score += 0.15
            elif "harvard" in combined_context:
                cluster.affiliation = "Harvard"
                disambiguation_score += 0.15
            
            cluster.disambiguation_confidence = min(1.0, disambiguation_score)
        
        return clusters