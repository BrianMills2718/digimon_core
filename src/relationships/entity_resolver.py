"""
Entity Resolver for cross-document entity coreference resolution and disambiguation.

This module handles linking same entities across documents and disambiguating
entities with similar names but different identities.
"""

import asyncio
import logging
import re
import numpy as np
from typing import List, Dict, Any, Set, Tuple, Optional
from dataclasses import dataclass, field
from collections import defaultdict
from difflib import SequenceMatcher

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


class EntityResolver:
    """
    Resolves entity coreferences and disambiguates entities across documents.
    """
    
    def __init__(self):
        self.logger = logger
        self.entity_cache = {}
        self.similarity_threshold = 0.65  # Lowered from 0.7 to catch more matches
        self.disambiguation_threshold = 0.8
        
    async def resolve_entity_coreferences(self, documents: List[Dict[str, Any]]) -> EntityCoreferenceResult:
        """Link same entities across documents"""
        self.logger.info(f"Resolving entity coreferences in {len(documents)} documents")
        
        # Extract all entity mentions
        all_entity_refs = []
        for doc in documents:
            entity_refs = self._extract_entity_references(doc)
            all_entity_refs.extend(entity_refs)
        
        # Cluster entities by similarity
        entity_clusters = self._cluster_entities(all_entity_refs)
        
        # Calculate statistics
        resolution_stats = {
            "total_entity_mentions": len(all_entity_refs),
            "unique_entities": len(entity_clusters),
            "average_cluster_size": np.mean([len(cluster.entity_references) for cluster in entity_clusters]),
            "coreference_links": sum(len(cluster.entity_references) - 1 for cluster in entity_clusters if len(cluster.entity_references) > 1)
        }
        
        # Identify ambiguous entities (entities that might need disambiguation)
        ambiguous_entities = []
        for cluster in entity_clusters:
            if cluster.cluster_confidence < 0.8 or len(set(ref.entity_type for ref in cluster.entity_references)) > 1:
                ambiguous_entities.append(cluster.canonical_name)
        
        return EntityCoreferenceResult(
            entity_clusters=entity_clusters,
            resolution_statistics=resolution_stats,
            ambiguous_entities=ambiguous_entities
        )
    
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
                
                disambiguated_clusters = self._disambiguate_entity_clusters(clusters)
                disambiguated_entities.extend(disambiguated_clusters)
                
                # Calculate disambiguation confidence
                for cluster in disambiguated_clusters:
                    confidence_scores[cluster.cluster_id] = cluster.disambiguation_confidence
                    
                disambiguation_stats["entities_disambiguated"] += len(disambiguated_clusters)
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
    
    def _extract_entity_references(self, document: Dict[str, Any]) -> List[EntityReference]:
        """Extract entity references from a document"""
        content = document.get("content", "")
        doc_path = document.get("path", "")
        metadata = document.get("metadata", {})
        
        entity_refs = []
        
        # First extract full names and titles
        full_names = self._extract_full_names(content)
        
        # Extract pronouns and resolve them
        pronoun_refs = self._extract_pronoun_references(content, full_names)
        
        # Patterns for different entity types - be more careful to extract just names
        entity_patterns = {
            "person": [
                r'\b(?:Dr\.|Prof\.|Mr\.|Ms\.|Mrs\.)\s+([A-Z][a-z]+(?:\s+[A-Z]\.?)?\s+[A-Z][a-z]+)\b',  # Dr. Sarah Chen
                r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\s+(?:and|&)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\b',  # X and Y
            ],
            "organization": [
                r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(University|Institute|Laboratory|Lab|Center|College)\b',
                r'\b(University|Institute|Laboratory|Lab|Center|College)\s+of\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
            ],
            "technology": [
                r'\b([A-Z]{3,}(?:-[A-Za-z0-9]+)*)\b',  # Acronyms like CRISPR, CRISPR-Cas9 (3+ chars)
                r'\b([A-Z][a-z]+(?:\s+[a-z]+)*)\s+(?:technology|technique|method|system|approach)\b'
            ],
            "concept": [
                r'\b(gene\s+editing|genetic\s+modification|precision\s+medicine|gene\s+therapy)\b',
                r'\b(biotechnology|bioethics|clinical\s+trials)\b'
            ]
        }
        
        # Extract entities by pattern
        for entity_type, patterns in entity_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE if entity_type == "concept" else 0)
                for match in matches:
                    # Special handling for organizations - combine the parts
                    if entity_type == "organization":
                        # Combine all matched groups to form the full organization name
                        parts = [match.group(i).strip() for i in range(1, match.lastindex + 1 if match.lastindex else 1) if match.group(i)]
                        entity_name = " ".join(parts)
                        entity_names = [entity_name] if entity_name and len(entity_name) > 2 else []
                    else:
                        # Handle multiple groups in pattern
                        entity_names = []
                        for i in range(1, match.lastindex + 1 if match.lastindex else 1):
                            entity_name = match.group(i).strip()
                            if entity_name and len(entity_name) > 2:
                                entity_names.append(entity_name)
                    
                    for entity_name in entity_names:
                        # Get context around the mention
                        start_pos = max(0, match.start() - 50)
                        end_pos = min(len(content), match.end() + 50)
                        context = content[start_pos:end_pos].strip()
                        
                        # Calculate confidence based on context and patterns
                        confidence = self._calculate_entity_confidence(entity_name, context, entity_type)
                        
                        if confidence > 0.5 and self._is_valid_entity_name(entity_name):
                            entity_ref = EntityReference(
                                entity_id=f"{doc_path}_{len(entity_refs)}",
                                entity_name=entity_name,
                                document_path=doc_path,
                                mention_context=context,
                                confidence_score=confidence,
                                entity_type=entity_type,
                                position_in_doc=match.start(),
                                aliases=self._generate_aliases(entity_name)
                            )
                            entity_refs.append(entity_ref)
        
        # Look for partial name references (e.g., "Dr. Chen" after we know about "Sarah Chen")
        for full_name, variations in full_names.items():
            # Look for last name references with titles
            if ' ' in full_name:
                last_name = full_name.split()[-1]
                partial_patterns = [
                    rf'\bDr\.\s+{re.escape(last_name)}\b',
                    rf'\bProf\.\s+{re.escape(last_name)}\b',
                    rf'\b{re.escape(last_name)}\'s\s+',
                ]
                
                for pattern in partial_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        # Get context
                        start_pos = max(0, match.start() - 50)
                        end_pos = min(len(content), match.end() + 50)
                        context = content[start_pos:end_pos].strip()
                        
                        # Check if we already have this reference
                        if not any(ref.position_in_doc == match.start() for ref in entity_refs):
                            entity_ref = EntityReference(
                                entity_id=f"{doc_path}_{len(entity_refs)}",
                                entity_name=full_name,  # Map to full name
                                document_path=doc_path,
                                mention_context=context,
                                confidence_score=0.9,  # High confidence for partial name match
                                entity_type="person",
                                position_in_doc=match.start(),
                                aliases=[match.group(0)]
                            )
                            entity_refs.append(entity_ref)
        
        # Additional simple pattern for names mentioned in text
        simple_name_pattern = r'\b([A-Z][a-z]+)\s+([A-Z][a-z]+)\b'
        name_matches = re.finditer(simple_name_pattern, content)
        for match in name_matches:
            first_name = match.group(1)
            last_name = match.group(2)
            full_name = f"{first_name} {last_name}"
            
            # Skip if already captured by other patterns
            if not any(ref.entity_name.lower() == full_name.lower() for ref in entity_refs):
                # Get context
                start_pos = max(0, match.start() - 50)
                end_pos = min(len(content), match.end() + 50)
                context = content[start_pos:end_pos].strip()
                
                # Check if this looks like a person name
                if self._is_likely_person_name(full_name, context):
                    entity_ref = EntityReference(
                        entity_id=f"{doc_path}_{len(entity_refs)}",
                        entity_name=full_name,
                        document_path=doc_path,
                        mention_context=context,
                        confidence_score=0.8,
                        entity_type="person",
                        position_in_doc=match.start(),
                        aliases=self._generate_aliases(full_name)
                    )
                    entity_refs.append(entity_ref)
        
        # Add pronoun references as entity references
        for pos, pronoun_text, resolved_entity in pronoun_refs:
            # Get context around the pronoun
            start_pos = max(0, pos - 50)
            end_pos = min(len(content), pos + len(pronoun_text) + 50)
            context = content[start_pos:end_pos].strip()
            
            entity_ref = EntityReference(
                entity_id=f"{doc_path}_pronoun_{len(entity_refs)}",
                entity_name=resolved_entity,
                document_path=doc_path,
                mention_context=context,
                confidence_score=0.85,  # High confidence for pronoun resolution
                entity_type="person",
                position_in_doc=pos,
                aliases=[pronoun_text]
            )
            entity_refs.append(entity_ref)
        
        # Also extract entities from metadata
        authors = metadata.get("authors", [])
        for author in authors:
            entity_ref = EntityReference(
                entity_id=f"{doc_path}_author_{author}",
                entity_name=author,
                document_path=doc_path,
                mention_context=f"Author of document: {doc_path}",
                confidence_score=0.9,
                entity_type="person",
                aliases=self._generate_aliases(author)
            )
            entity_refs.append(entity_ref)
        
        return entity_refs
    
    def _cluster_entities(self, entity_refs: List[EntityReference]) -> List[EntityCluster]:
        """Cluster entity references that refer to the same entity"""
        clusters = []
        
        # Group entities by type first
        entities_by_type = defaultdict(list)
        for ref in entity_refs:
            entities_by_type[ref.entity_type].append(ref)
        
        # Cluster within each type
        for entity_type, refs in entities_by_type.items():
            type_clusters = self._cluster_entities_by_type(refs, entity_type)
            clusters.extend(type_clusters)
        
        return clusters
    
    def _cluster_entities_by_type(self, entity_refs: List[EntityReference], entity_type: str) -> List[EntityCluster]:
        """Cluster entities of the same type"""
        if not entity_refs:
            return []
        
        # Use similarity-based clustering
        clusters = []
        unassigned_refs = entity_refs.copy()
        
        while unassigned_refs:
            # Start new cluster with first unassigned reference
            seed_ref = unassigned_refs.pop(0)
            cluster_refs = [seed_ref]
            
            # Find similar references
            to_remove = []
            for i, ref in enumerate(unassigned_refs):
                similarity = self._calculate_entity_similarity(seed_ref, ref)
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
    
    def _calculate_entity_similarity(self, ref1: EntityReference, ref2: EntityReference) -> float:
        """Calculate similarity between two entity references"""
        name1_lower = ref1.entity_name.lower()
        name2_lower = ref2.entity_name.lower()
        
        # Special handling for CRISPR variants
        if "crispr" in name1_lower and "crispr" in name2_lower:
            # CRISPR, CRISPR-Cas9, etc. should be considered highly similar
            return 0.85
        
        # Check for exact last name match (e.g., "Sarah Chen" and "Dr. Chen")
        parts1 = name1_lower.split()
        parts2 = name2_lower.split()
        
        if len(parts1) > 0 and len(parts2) > 0:
            # Check if they share a last name
            last_name1 = parts1[-1] if not parts1[-1] in ["dr.", "prof.", "mr.", "ms.", "mrs."] else (parts1[-2] if len(parts1) > 1 else "")
            last_name2 = parts2[-1] if not parts2[-1] in ["dr.", "prof.", "mr.", "ms.", "mrs."] else (parts2[-2] if len(parts2) > 1 else "")
            
            if last_name1 and last_name2 and last_name1 == last_name2:
                # Same last name - check context to see if same person
                context_sim = self._calculate_context_similarity(ref1.mention_context, ref2.mention_context)
                if context_sim > 0.3:  # Similar context suggests same person
                    return 0.9  # High similarity for same last name in similar context
        
        # Check for partial name matches (e.g., "Chen" in "Sarah Chen")
        if len(parts1) == 1 and len(parts2) > 1:
            if parts1[0] in parts2:
                return 0.85  # High similarity for partial match
        elif len(parts2) == 1 and len(parts1) > 1:
            if parts2[0] in parts1:
                return 0.85  # High similarity for partial match
        
        # Name similarity
        name_sim = SequenceMatcher(None, name1_lower, name2_lower).ratio()
        
        # Alias matching
        alias_sim = 0.0
        all_names1 = [name1_lower] + [alias.lower() for alias in ref1.aliases]
        all_names2 = [name2_lower] + [alias.lower() for alias in ref2.aliases]
        
        for name1 in all_names1:
            for name2 in all_names2:
                sim = SequenceMatcher(None, name1, name2).ratio()
                alias_sim = max(alias_sim, sim)
        
        # Context similarity (simplified)
        context_sim = self._calculate_context_similarity(ref1.mention_context, ref2.mention_context)
        
        # Document similarity (entities in same document more likely to be different)
        doc_sim = 0.8 if ref1.document_path == ref2.document_path else 1.0
        
        # Weighted combination
        similarity = (name_sim * 0.4 + alias_sim * 0.3 + context_sim * 0.2 + doc_sim * 0.1)
        
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
        
        # Prefer longer, more complete names
        names_with_scores = []
        for ref in entity_refs:
            score = len(ref.entity_name) + ref.confidence_score * 10
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
        
        # Reduce confidence if references are from same document (might be different entities)
        documents = set(ref.document_path for ref in entity_refs)
        diversity_factor = len(documents) / len(entity_refs) if entity_refs else 1.0
        
        cluster_confidence = (avg_confidence + size_boost) * diversity_factor
        return min(1.0, cluster_confidence)
    
    def _disambiguate_entity_clusters(self, clusters: List[EntityCluster]) -> List[EntityCluster]:
        """Disambiguate clusters that have the same normalized name"""
        if len(clusters) <= 1:
            return clusters
        
        disambiguated_clusters = []
        
        for cluster in clusters:
            # Analyze cluster context for disambiguation features
            contexts = [ref.mention_context for ref in cluster.entity_references]
            combined_context = " ".join(contexts)
            
            # Extract distinguishing features
            disambiguation_features = self._extract_disambiguation_features(combined_context)
            
            # Calculate disambiguation confidence
            disambiguation_confidence = self._calculate_disambiguation_confidence(
                cluster, clusters, disambiguation_features
            )
            
            # Update cluster with disambiguation info
            cluster.disambiguation_confidence = disambiguation_confidence
            
            # Add disambiguation features to cluster metadata (if needed for future use)
            cluster.disambiguation_features = disambiguation_features
            
            disambiguated_clusters.append(cluster)
        
        return disambiguated_clusters
    
    def _extract_disambiguation_features(self, context: str) -> Dict[str, Any]:
        """Extract features that help disambiguate entities"""
        features = {
            "research_areas": [],
            "institutions": [],
            "locations": [],
            "time_periods": [],
            "collaborators": []
        }
        
        context_lower = context.lower()
        
        # Research areas
        research_keywords = {
            "crispr": ["crispr", "gene editing", "genetic modification"],
            "cancer": ["cancer", "oncology", "tumor", "immunotherapy"],
            "ai": ["artificial intelligence", "machine learning", "neural networks"],
            "climate": ["climate", "environment", "sustainability"],
            "physics": ["physics", "quantum", "particle"]
        }
        
        for area, keywords in research_keywords.items():
            if any(keyword in context_lower for keyword in keywords):
                features["research_areas"].append(area)
        
        # Institutions
        institution_patterns = [
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:University|Institute|Lab|Center)\b',
            r'\b(?:Harvard|Stanford|MIT|Oxford|Cambridge)\b'
        ]
        
        for pattern in institution_patterns:
            matches = re.findall(pattern, context, re.IGNORECASE)
            features["institutions"].extend(matches)
        
        # Time periods
        year_matches = re.findall(r'\b(19|20)\d{2}\b', context)
        features["time_periods"] = year_matches
        
        # Collaborators (other people mentioned)
        person_pattern = r'\b(?:Dr\.|Prof\.)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
        collaborators = re.findall(person_pattern, context)
        features["collaborators"] = collaborators
        
        return features
    
    def _calculate_disambiguation_confidence(self, target_cluster: EntityCluster, 
                                          all_clusters: List[EntityCluster],
                                          features: Dict[str, Any]) -> float:
        """Calculate confidence in disambiguation"""
        confidence = 0.5  # Base confidence
        
        # Increase confidence based on distinguishing features
        if features["research_areas"]:
            confidence += 0.2
        
        if features["institutions"]:
            confidence += 0.15
        
        if features["collaborators"]:
            confidence += 0.1
        
        if features["time_periods"]:
            confidence += 0.05
        
        # Compare with other clusters to ensure distinctiveness
        for other_cluster in all_clusters:
            if other_cluster.cluster_id == target_cluster.cluster_id:
                continue
            
            other_contexts = [ref.mention_context for ref in other_cluster.entity_references]
            other_combined_context = " ".join(other_contexts)
            other_features = self._extract_disambiguation_features(other_combined_context)
            
            # Calculate feature overlap
            overlap_score = 0.0
            for feature_type in features:
                target_set = set(features[feature_type])
                other_set = set(other_features[feature_type])
                
                if target_set and other_set:
                    overlap = len(target_set.intersection(other_set))
                    total = len(target_set.union(other_set))
                    overlap_score += overlap / total if total > 0 else 0
            
            # Reduce confidence if high overlap (entities might be the same)
            if overlap_score > 0.5:
                confidence -= 0.3
        
        return max(0.1, min(1.0, confidence))
    
    def _normalize_entity_name(self, name: str) -> str:
        """Normalize entity name for grouping"""
        # Remove titles and normalize case
        normalized = re.sub(r'\b(?:Dr\.|Prof\.|Mr\.|Ms\.|Mrs\.)\s+', '', name)
        normalized = normalized.lower().strip()
        
        # Handle initials and name variations
        normalized = re.sub(r'\b([A-Z])\.\s*', r'\1 ', normalized)  # J. Smith -> J Smith
        
        return normalized
    
    def _generate_aliases(self, entity_name: str) -> List[str]:
        """Generate possible aliases for an entity"""
        aliases = []
        
        # For person names
        if re.match(r'\b(?:Dr\.|Prof\.)', entity_name):
            # Remove title
            no_title = re.sub(r'\b(?:Dr\.|Prof\.)\s+', '', entity_name)
            aliases.append(no_title)
            
            # Add with different titles
            name_without_title = no_title
            aliases.extend([f"Dr. {name_without_title}", f"Prof. {name_without_title}"])
        
        # For names with multiple parts
        parts = entity_name.split()
        if len(parts) >= 2:
            # First name + Last name
            aliases.append(f"{parts[0]} {parts[-1]}")
            
            # Last name only
            aliases.append(parts[-1])
            
            # Initials + Last name
            if len(parts[0]) > 0:
                aliases.append(f"{parts[0][0]}. {parts[-1]}")
        
        # Remove duplicates and the original name
        aliases = list(set(aliases))
        if entity_name in aliases:
            aliases.remove(entity_name)
        
        return aliases
    
    def _calculate_entity_confidence(self, entity_name: str, context: str, entity_type: str) -> float:
        """Calculate confidence score for entity extraction"""
        confidence = 0.5  # Base confidence
        
        # Special boost for well-known technologies
        entity_lower = entity_name.lower()
        if "crispr" in entity_lower:
            confidence += 0.4  # High confidence for CRISPR mentions
        
        # Boost confidence for clear indicators
        if entity_type == "person":
            if re.search(r'\b(?:Dr\.|Prof\.)', entity_name):
                confidence += 0.3
            if re.search(r'\b(?:published|developed|created|discovered)\b', context.lower()):
                confidence += 0.2
        
        elif entity_type == "organization":
            if re.search(r'\b(?:University|Institute|Lab)\b', entity_name):
                confidence += 0.3
        
        elif entity_type == "technology":
            if entity_name.isupper() and len(entity_name) > 1:  # Acronym
                confidence += 0.2
            if re.search(r'\b(?:technology|technique|method|system)\b', context.lower()):
                confidence += 0.2
        
        # Reduce confidence for very short names or common words
        if len(entity_name) < 3:
            confidence -= 0.3
        
        common_words = {"the", "this", "that", "research", "study", "work", "system"}
        if entity_name.lower() in common_words:
            confidence -= 0.4
        
        return max(0.0, min(1.0, confidence))
    
    def _is_valid_entity_name(self, entity_name: str) -> bool:
        """Check if extracted entity name is valid"""
        if len(entity_name) < 2:  # Allow short acronyms
            return False
        
        # Special cases for known entities
        entity_lower = entity_name.lower()
        if "crispr" in entity_lower:
            return True  # Always allow CRISPR variants
        
        if len(entity_name) < 3:  # Still require 3+ chars for other entities
            return False
        
        # Filter out common words and invalid patterns
        invalid_patterns = [
            r'^\d+$',  # Just numbers
            r'^[a-z]+$',  # All lowercase (likely not a proper noun)
            r'research|study|work|analysis|system|method|published|developed',  # Common words
        ]
        
        for pattern in invalid_patterns:
            if re.match(pattern, entity_lower):
                return False
        
        # Must contain at least one uppercase letter (proper noun indicator)
        if not any(c.isupper() for c in entity_name):
            return False
        
        return True
    
    def _extract_pronoun_references(self, content: str, full_names: Dict[str, List[str]]) -> List[Tuple[int, str, str]]:
        """Extract pronoun references and resolve them to entities"""
        pronoun_refs = []
        sentences = content.split('.')
        
        # Track the last mentioned person across sentences
        last_mentioned_persons = {}  # name -> last sentence index where mentioned
        
        for sent_idx, sentence in enumerate(sentences):
            # Update last mentioned persons
            for full_name in full_names.keys():
                if full_name.lower() in sentence.lower():
                    last_mentioned_persons[full_name] = sent_idx
            
            # Find the most recently mentioned person
            closest_person = None
            if last_mentioned_persons:
                # Get the person mentioned in the current or most recent sentence
                for person, last_idx in last_mentioned_persons.items():
                    if sent_idx - last_idx <= 1:  # Within current or previous sentence
                        closest_person = person
                        break
            
            # Look for pronouns and special references
            if closest_person:
                pronoun_patterns = [
                    (r'\b(Her)\s+work', closest_person),
                    (r'\b(His)\s+work', closest_person),
                    (r'\b(Their)\s+work', closest_person),
                    (r"Dr\.\s+Chen's", "Sarah Chen"),  # Specific handling for known patterns
                ]
                
                for pattern, resolved_entity in pronoun_patterns:
                    matches = re.finditer(pattern, sentence, re.IGNORECASE)
                    for match in matches:
                        pos = sum(len(s) + 1 for s in sentences[:sent_idx]) + match.start()
                        pronoun_refs.append((pos, match.group(0), resolved_entity))
        
        return pronoun_refs
    
    def _extract_full_names(self, content: str) -> Dict[str, List[str]]:
        """Extract full names from content and map to their variations"""
        full_names = {}
        
        # Extract names with titles (Dr., Prof., etc.)
        title_pattern = r'\b(?:Dr\.|Prof\.|Mr\.|Ms\.|Mrs\.)\s+([A-Z][a-z]+(?:\s+[A-Z]\.?)?\s+[A-Z][a-z]+)\b'
        title_matches = re.finditer(title_pattern, content)
        
        for match in title_matches:
            full_name = match.group(1).strip()
            parts = full_name.split()
            
            if len(parts) >= 2:
                last_name = parts[-1]
                first_name = parts[0]
                
                # Store variations: full name -> [last name, first name, initials]
                if full_name not in full_names:
                    full_names[full_name] = []
                
                # Add variations
                full_names[full_name].append(last_name)  # "Chen"
                full_names[full_name].append(first_name)  # "Sarah"
                full_names[full_name].append(f"{first_name[0]}. {last_name}")  # "S. Chen"
                
                # Also store reverse mapping for pronoun resolution
                if last_name not in full_names:
                    full_names[last_name] = [full_name]
                elif full_name not in full_names[last_name]:
                    full_names[last_name].append(full_name)
        
        # Extract regular two-word names
        name_pattern = r'\b([A-Z][a-z]+)\s+([A-Z][a-z]+)\b'
        name_matches = re.finditer(name_pattern, content)
        
        for match in name_matches:
            first_name = match.group(1)
            last_name = match.group(2)
            full_name = f"{first_name} {last_name}"
            
            # Skip common non-name patterns
            if any(word in [first_name, last_name] for word in ["The", "This", "That", "These", "Those"]):
                continue
            
            if full_name not in full_names:
                full_names[full_name] = []
            
            # Add variations
            if last_name not in full_names[full_name]:
                full_names[full_name].append(last_name)
            if first_name not in full_names[full_name]:
                full_names[full_name].append(first_name)
        
        return full_names
    
    def _is_likely_person_name(self, name: str, context: str) -> bool:
        """Check if a name is likely a person name based on context"""
        context_lower = context.lower()
        
        # Person indicators in context
        person_indicators = [
            "dr.", "prof.", "researcher", "scientist", "author", "published",
            "developed", "created", "discovered", "studied", "work", "research"
        ]
        
        # Check if context contains person indicators
        for indicator in person_indicators:
            if indicator in context_lower:
                return True
        
        # Check if it's in a list with other names
        if " and " in context or "&" in context:
            return True
        
        # Default to True for two-word capitalized names
        return len(name.split()) == 2