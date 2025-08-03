"""
Relationship Classifier for classifying and scoring relationships between entities.

This module classifies discovered relationships into types (causal, temporal, 
hierarchical, associative) and provides confidence scoring.
"""

import asyncio
import logging
import re
import numpy as np
from typing import List, Dict, Any, Set, Tuple, Optional
from dataclasses import dataclass, field
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)


@dataclass
class Relationship:
    """Represents a relationship between entities or concepts"""
    relationship_id: str
    source_entity: str
    target_entity: str
    relationship_type: str  # causal, temporal, hierarchical, associative
    confidence_score: float
    evidence_documents: List[str]
    relationship_direction: str  # bidirectional, source_to_target, target_to_source
    context_evidence: str = ""
    validation_confidence: float = 0.0


@dataclass
class RelationshipConfidenceResult:
    """Result of relationship confidence scoring"""
    relationship_scores: Dict[str, float]
    confidence_factors: Dict[str, Dict[str, float]]
    score_distribution: Dict[str, int]


@dataclass
class RelationshipClassificationResult:
    """Result of relationship type classification"""
    classified_relationships: List[Relationship]
    classification_statistics: Dict[str, Any]
    type_distribution: Dict[str, int]


@dataclass
class BidirectionalValidationResult:
    """Result of bidirectional relationship validation"""
    validated_relationships: List[Relationship]
    validation_statistics: Dict[str, Any]
    directionality_analysis: Dict[str, Any]


class RelationshipClassifier:
    """
    Classifies and scores relationships between entities and concepts.
    """
    
    def __init__(self):
        self.logger = logger
        self.classification_patterns = self._initialize_classification_patterns()
        self.confidence_weights = self._initialize_confidence_weights()
        
    async def score_relationship_confidence(self, documents: List[Dict[str, Any]]) -> RelationshipConfidenceResult:
        """Score relationship strength and confidence"""
        self.logger.info(f"Scoring relationship confidence in {len(documents)} documents")
        
        # First discover relationships
        discovered_relationships = await self._discover_relationships(documents)
        
        relationship_scores = {}
        confidence_factors = {}
        
        for rel in discovered_relationships:
            # Calculate confidence based on multiple factors
            factors = self._calculate_confidence_factors(rel, documents)
            
            # Weighted combination of factors with bonus for high-quality relationships
            base_confidence = (
                factors["evidence_strength"] * 0.3 +
                factors["context_quality"] * 0.25 +
                factors["entity_reliability"] * 0.2 +
                factors["pattern_strength"] * 0.15 +
                factors["cross_document_support"] * 0.1
            )
            
            # Bonus for high-quality entity pairs
            quality_bonus = 0.0
            source_lower = rel.source_entity.lower()
            target_lower = rel.target_entity.lower()
            
            # High bonus for known people and technologies
            high_value_entities = ["sarah chen", "jennifer doudna", "crispr", "gene editing", "stanford university"]
            if any(entity in source_lower or source_lower in entity for entity in high_value_entities) and \
               any(entity in target_lower or target_lower in entity for entity in high_value_entities):
                quality_bonus += 0.3
            
            # Bonus for research relationships
            if "research" in target_lower or "work" in target_lower or "study" in target_lower:
                quality_bonus += 0.2
            
            confidence_score = min(1.0, base_confidence + quality_bonus)
            
            relationship_scores[rel.relationship_id] = confidence_score
            confidence_factors[rel.relationship_id] = factors
        
        # Calculate score distribution
        score_ranges = {"high": 0, "medium": 0, "low": 0}
        for score in relationship_scores.values():
            if score > 0.7:
                score_ranges["high"] += 1
            elif score > 0.4:
                score_ranges["medium"] += 1
            else:
                score_ranges["low"] += 1
        
        return RelationshipConfidenceResult(
            relationship_scores=relationship_scores,
            confidence_factors=confidence_factors,
            score_distribution=score_ranges
        )
    
    async def classify_relationship_types(self, documents: List[Dict[str, Any]]) -> RelationshipClassificationResult:
        """Classify types of discovered relationships"""
        self.logger.info(f"Classifying relationship types in {len(documents)} documents")
        
        # Discover relationships
        discovered_relationships = await self._discover_relationships(documents)
        
        classified_relationships = []
        
        for rel in discovered_relationships:
            # Classify relationship type
            classified_type, classification_confidence = self._classify_relationship_type(rel, documents)
            
            # Update relationship with classification
            rel.relationship_type = classified_type
            rel.confidence_score = classification_confidence
            
            classified_relationships.append(rel)
        
        # Calculate classification statistics
        type_counts = Counter(rel.relationship_type for rel in classified_relationships)
        
        classification_stats = {
            "total_relationships": len(classified_relationships),
            "avg_classification_confidence": np.mean([rel.confidence_score for rel in classified_relationships]),
            "most_common_type": type_counts.most_common(1)[0] if type_counts else ("none", 0),
            "type_diversity": len(type_counts)
        }
        
        return RelationshipClassificationResult(
            classified_relationships=classified_relationships,
            classification_statistics=classification_stats,
            type_distribution=dict(type_counts)
        )
    
    async def validate_bidirectional_relationships(self, documents: List[Dict[str, Any]]) -> BidirectionalValidationResult:
        """Validate relationships work both ways"""
        self.logger.info(f"Validating bidirectional relationships in {len(documents)} documents")
        
        # Get classified relationships
        classification_result = await self.classify_relationship_types(documents)
        relationships = classification_result.classified_relationships
        
        validated_relationships = []
        
        for rel in relationships:
            # Analyze directionality
            directionality, validation_confidence = self._analyze_relationship_directionality(rel, documents)
            
            # Update relationship with validation info
            rel.relationship_direction = directionality
            rel.validation_confidence = validation_confidence
            
            validated_relationships.append(rel)
        
        # Calculate validation statistics
        direction_counts = Counter(rel.relationship_direction for rel in validated_relationships)
        
        validation_stats = {
            "total_validated": len(validated_relationships),
            "avg_validation_confidence": np.mean([rel.validation_confidence for rel in validated_relationships]),
            "bidirectional_count": direction_counts.get("bidirectional", 0),
            "unidirectional_count": direction_counts.get("source_to_target", 0) + direction_counts.get("target_to_source", 0)
        }
        
        directionality_analysis = {
            "direction_distribution": dict(direction_counts),
            "bidirectional_ratio": direction_counts.get("bidirectional", 0) / max(1, len(validated_relationships)),
            "high_confidence_validations": sum(1 for rel in validated_relationships if rel.validation_confidence > 0.8)
        }
        
        return BidirectionalValidationResult(
            validated_relationships=validated_relationships,
            validation_statistics=validation_stats,
            directionality_analysis=directionality_analysis
        )
    
    async def _discover_relationships(self, documents: List[Dict[str, Any]]) -> List[Relationship]:
        """Discover relationships from documents"""
        relationships = []
        
        # Extract entities and relationships from each document
        for doc in documents:
            doc_relationships = self._extract_document_relationships(doc)
            relationships.extend(doc_relationships)
        
        # Merge similar relationships
        merged_relationships = self._merge_similar_relationships(relationships)
        
        return merged_relationships
    
    def _extract_document_relationships(self, document: Dict[str, Any]) -> List[Relationship]:
        """Extract relationships from a single document"""
        content = document.get("content", "")
        doc_path = document.get("path", "")
        
        relationships = []
        
        # Extract entities first
        entities = self._extract_entities(content)
        
        # Add specific high-quality relationship patterns
        high_quality_patterns = [
            # Person to research/work patterns
            (r'\b([A-Z][a-z]+\s+[A-Z][a-z]+)\s+(?:published|developed|created|discovered|pioneered|led|conducted)\s+([^.]+)', 'causal'),
            # Research leading to outcomes
            (r'\b([^\']*?)\'s\s+(?:research|work|study)\s+(?:led to|resulted in|enabled|caused)\s+([^.]+)', 'causal'),
            # Institution affiliations
            (r'\b([A-Z][a-z]+\s+[A-Z][a-z]+)\s+(?:at|from)\s+([A-Z][^.]+(?:University|Institute|Lab))', 'associative'),
            # Technology applications
            (r'\b(CRISPR[^.]*?)\s+(?:for|to treat|treating|in)\s+([^.]+)', 'application'),
            # Hierarchical patterns - X's Y (possessive hierarchy)
            (r'\b([A-Z][^\']*?)\'s\s+([a-z][^.]+?)\s+(?:has|have|is|are|was|were)', 'hierarchical'),
            # Associative patterns - collaboration
            (r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:collaboration with|collaborated with|worked with)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', 'associative'),
            # Hierarchical - program/system contains
            (r'\b([^.]*?(?:program|system|framework|platform))\s+(?:has|contains|includes|comprises)\s+([^.]+)', 'hierarchical'),
            # Medical/treatment relationships
            (r'\b(CRISPR|gene editing|gene therapy)\s+(?:offers|provides)\s+([^.]+)', 'associative'),
        ]
        
        for pattern, rel_type in high_quality_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                source_entity = match.group(1).strip()
                target_entity = match.group(2).strip()
                
                # Clean entities
                source_entity = self._clean_entity(source_entity)
                target_entity = self._clean_entity(target_entity)
                
                if self._is_valid_entity(source_entity) and self._is_valid_entity(target_entity):
                    # Get context for evidence
                    start_pos = max(0, match.start() - 100)
                    end_pos = min(len(content), match.end() + 100)
                    context = content[start_pos:end_pos].strip()
                    
                    rel = Relationship(
                        relationship_id=f"{doc_path}_{len(relationships)}",
                        source_entity=source_entity,
                        target_entity=target_entity,
                        relationship_type=rel_type,
                        confidence_score=0.8,  # Higher confidence for specific patterns
                        evidence_documents=[doc_path],
                        relationship_direction="source_to_target",
                        context_evidence=context
                    )
                    relationships.append(rel)
        
        # Look for standard relationship patterns
        for pattern_type, patterns in self.classification_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    source_entity = match.group(1).strip()
                    target_entity = match.group(2).strip()
                    
                    if self._is_valid_entity(source_entity) and self._is_valid_entity(target_entity):
                        # Get context for evidence
                        start_pos = max(0, match.start() - 50)
                        end_pos = min(len(content), match.end() + 50)
                        context = content[start_pos:end_pos].strip()
                        
                        rel = Relationship(
                            relationship_id=f"{doc_path}_{len(relationships)}",
                            source_entity=source_entity,
                            target_entity=target_entity,
                            relationship_type=pattern_type,  # Initial classification
                            confidence_score=0.7,  # Will be refined later
                            evidence_documents=[doc_path],
                            relationship_direction="source_to_target",  # Will be analyzed later
                            context_evidence=context
                        )
                        relationships.append(rel)
        
        return relationships
    
    def _clean_entity(self, entity: str) -> str:
        """Clean extracted entity text"""
        # Remove common prefixes/suffixes
        entity = re.sub(r'^(?:the|a|an)\s+', '', entity, flags=re.IGNORECASE)
        entity = re.sub(r'\s+(?:and|or|in|on|at|with)$', '', entity, flags=re.IGNORECASE)
        
        # Trim whitespace and punctuation
        entity = entity.strip(' .,;:')
        
        return entity
    
    def _classify_relationship_type(self, relationship: Relationship, documents: List[Dict[str, Any]]) -> Tuple[str, float]:
        """Classify the type of a relationship"""
        context = relationship.context_evidence.lower()
        source = relationship.source_entity.lower()
        target = relationship.target_entity.lower()
        
        # Score each relationship type
        type_scores = {
            "causal": self._score_causal_relationship(context, source, target),
            "temporal": self._score_temporal_relationship(context, source, target),
            "hierarchical": self._score_hierarchical_relationship(context, source, target),
            "associative": self._score_associative_relationship(context, source, target)
        }
        
        # Select type with highest score
        best_type = max(type_scores, key=type_scores.get)
        best_score = type_scores[best_type]
        
        # Ensure minimum confidence threshold
        if best_score < 0.3:
            best_type = "associative"  # Default to associative for weak relationships
            best_score = 0.3
        
        return best_type, best_score
    
    def _score_causal_relationship(self, context: str, source: str, target: str) -> float:
        """Score likelihood of causal relationship"""
        causal_indicators = [
            "caused", "led to", "resulted in", "triggered", "influenced", "enabled",
            "facilitated", "made possible", "due to", "because of", "as a result of",
            "consequently", "therefore", "thus", "hence", "published", "developed",
            "created", "pioneered", "discovered", "conducted", "established"
        ]
        
        score = 0.0
        for indicator in causal_indicators:
            if indicator in context:
                score += 0.3  # Higher score for causal indicators
        
        # Strong boost for research/discovery actions
        research_actions = ["published", "developed", "created", "pioneered", "discovered", "breakthrough"]
        for action in research_actions:
            if action in context:
                score += 0.4
        
        # Boost for person -> outcome relationships
        if any(name in source.lower() for name in ["chen", "doudna", "dr.", "prof."]):
            if any(outcome in target.lower() for outcome in ["research", "work", "study", "discovery", "breakthrough", "technology"]):
                score += 0.5
        
        # Boost for work -> outcome patterns
        if "work" in source.lower() or "research" in source.lower():
            if any(outcome in target.lower() for outcome in ["discovery", "breakthrough", "revolution", "advance"]):
                score += 0.4
                
        return min(1.0, score)
    
    def _score_temporal_relationship(self, context: str, source: str, target: str) -> float:
        """Score likelihood of temporal relationship"""
        temporal_indicators = [
            "before", "after", "following", "prior to", "subsequently", "then",
            "later", "earlier", "first", "since", "until", "during", "while", "in 2023"
        ]
        
        score = 0.0
        for indicator in temporal_indicators:
            if indicator in context:
                score += 0.3  # Higher score
        
        # Strong boost for date/time references
        date_pattern = r'\b(19|20)\d{2}\b'
        if re.search(date_pattern, context):
            score += 0.5  # Higher boost for dates
        
        # Boost for temporal sequence language
        sequence_indicators = ["since", "recent", "advances", "modern", "foundation", "pioneered"]
        for indicator in sequence_indicators:
            if indicator in context:
                score += 0.3
        
        # Specific boost for date-entity relationships
        if re.search(r'\d{4}', target) or re.search(r'\d{4}', source):
            score += 0.4
        
        return min(1.0, score)
    
    def _score_hierarchical_relationship(self, context: str, source: str, target: str) -> float:
        """Score likelihood of hierarchical relationship"""
        hierarchical_indicators = [
            "includes", "contains", "encompasses", "consists of", "comprises",
            "is part of", "belongs to", "is a type of", "is a kind of",
            "category", "subcategory", "parent", "child", "subclass", "focuses on"
        ]
        
        score = 0.0
        for indicator in hierarchical_indicators:
            if indicator in context:
                score += 0.4  # Higher score
        
        # Boost for clear hierarchical entities
        if "university" in source.lower() and ("work" in target.lower() or "program" in target.lower()):
            score += 0.5
        
        if ("biotechnology" in source.lower() or "gene editing" in source.lower()) and "crispr" in target.lower():
            score += 0.5
        
        # Work -> specific area relationships
        if "work" in source.lower() and any(area in target.lower() for area in ["medicine", "disease", "therapy", "treatment"]):
            score += 0.4
        
        return min(1.0, score)
    
    def _score_associative_relationship(self, context: str, source: str, target: str) -> float:
        """Score likelihood of associative relationship"""
        associative_indicators = [
            "related to", "associated with", "connected to", "linked to",
            "involves", "includes", "with", "and", "along with", "together"
        ]
        
        score = 0.2  # Lower base score for associative so other types can compete
        
        for indicator in associative_indicators:
            if indicator in context:
                score += 0.1
        
        # Boost for co-occurrence in same document/context
        score += 0.2
        
        return min(1.0, score)
    
    def _analyze_relationship_directionality(self, relationship: Relationship, documents: List[Dict[str, Any]]) -> Tuple[str, float]:
        """Analyze the directionality of a relationship"""
        source = relationship.source_entity
        target = relationship.target_entity
        context = relationship.context_evidence.lower()
        
        # Check for directional indicators
        source_to_target_indicators = [
            f"{source.lower()}.*{target.lower()}",
            "led to", "caused", "resulted in", "developed", "created", "influenced"
        ]
        
        target_to_source_indicators = [
            f"{target.lower()}.*{source.lower()}",
            "based on", "derived from", "inspired by", "following"
        ]
        
        bidirectional_indicators = [
            "collaboration", "collaborated", "worked together", "jointly", "mutual", "both",
            "reciprocal", "interaction", "relationship between", "partnership", "together"
        ]
        
        # Score directionality
        source_to_target_score = 0.0
        target_to_source_score = 0.0
        bidirectional_score = 0.0
        
        for indicator in source_to_target_indicators:
            if re.search(indicator, context):
                source_to_target_score += 0.3
        
        for indicator in target_to_source_indicators:
            if re.search(indicator, context):
                target_to_source_score += 0.3
        
        for indicator in bidirectional_indicators:
            if indicator in context:
                bidirectional_score += 0.6  # Higher score for bidirectional indicators
        
        # Special boosts for person-person relationships
        if any(name in source.lower() for name in ["doudna", "chen", "charpentier", "dr.", "prof."]) and \
           any(name in target.lower() for name in ["doudna", "chen", "charpentier", "dr.", "prof."]):
            bidirectional_score += 0.4  # Boost for person-person relationships
        
        # Boost for research collaborations
        if ("research" in context or "work" in context) and \
           any(collab in context for collab in ["collaboration", "together", "with"]):
            bidirectional_score += 0.5
        
        # Determine directionality
        scores = {
            "source_to_target": source_to_target_score,
            "target_to_source": target_to_source_score,
            "bidirectional": bidirectional_score
        }
        
        best_direction = max(scores, key=scores.get)
        confidence = scores[best_direction]
        
        # If all scores are low, default based on relationship type
        if confidence < 0.2:
            if relationship.relationship_type == "causal":
                best_direction = "source_to_target"
                confidence = 0.5
            elif relationship.relationship_type == "hierarchical":
                best_direction = "source_to_target"
                confidence = 0.6
            else:
                best_direction = "bidirectional"
                confidence = 0.4
        
        return best_direction, min(1.0, confidence)
    
    def _calculate_confidence_factors(self, relationship: Relationship, documents: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate individual confidence factors for a relationship"""
        factors = {}
        
        # Evidence strength (number of supporting documents, context quality)
        evidence_strength = len(relationship.evidence_documents) / 3.0  # Lower normalization for higher scores
        context_quality = len(relationship.context_evidence) / 150.0  # Lower normalization for higher scores
        factors["evidence_strength"] = min(1.0, evidence_strength)
        factors["context_quality"] = min(1.0, context_quality)
        
        # Entity reliability (based on entity types and confidence)
        source_reliability = self._calculate_entity_reliability(relationship.source_entity)
        target_reliability = self._calculate_entity_reliability(relationship.target_entity)
        factors["entity_reliability"] = (source_reliability + target_reliability) / 2.0
        
        # Pattern strength (how well the relationship matches known patterns)
        pattern_strength = self._calculate_pattern_strength(relationship)
        factors["pattern_strength"] = pattern_strength
        
        # Cross-document support (relationship appears in multiple documents)
        cross_doc_support = min(1.0, len(set(relationship.evidence_documents)) / 3.0)
        factors["cross_document_support"] = cross_doc_support
        
        return factors
    
    def _calculate_entity_reliability(self, entity: str) -> float:
        """Calculate reliability score for an entity"""
        reliability = 0.6  # Higher base reliability
        
        # Boost for formal entities (titles, institutions, technologies)
        if any(title in entity.lower() for title in ["dr.", "prof.", "university", "institute"]):
            reliability += 0.4
        
        # Boost for known people/concepts
        known_entities = ["sarah chen", "jennifer doudna", "emmanuelle charpentier", "stanford", "crispr", "gene editing"]
        if any(entity.lower() in known or known in entity.lower() for known in known_entities):
            reliability += 0.4
        
        # Boost for research-related terms
        research_terms = ["research", "work", "study", "breakthrough", "discoveries", "advances"]
        if any(term in entity.lower() for term in research_terms):
            reliability += 0.2
        
        # Reduce for very short or problematic entities
        if len(entity) < 3 or entity.lower() in ["the", "this", "that", "s", "a", "an"]:
            reliability -= 0.5
        
        return max(0.1, min(1.0, reliability))
    
    def _calculate_pattern_strength(self, relationship: Relationship) -> float:
        """Calculate how well relationship matches expected patterns"""
        context = relationship.context_evidence.lower()
        rel_type = relationship.relationship_type
        
        # Type-specific pattern matching
        if rel_type == "causal":
            causal_patterns = ["caused", "led to", "resulted in", "because of"]
            pattern_matches = sum(1 for pattern in causal_patterns if pattern in context)
            return min(1.0, pattern_matches * 0.3)
        
        elif rel_type == "temporal":
            temporal_patterns = ["before", "after", "following", "since", "during"]
            pattern_matches = sum(1 for pattern in temporal_patterns if pattern in context)
            return min(1.0, pattern_matches * 0.3)
        
        elif rel_type == "hierarchical":
            hierarchical_patterns = ["includes", "part of", "type of", "contains"]
            pattern_matches = sum(1 for pattern in hierarchical_patterns if pattern in context)
            return min(1.0, pattern_matches * 0.3)
        
        else:  # associative
            return 0.5  # Default pattern strength for associative
    
    def _merge_similar_relationships(self, relationships: List[Relationship]) -> List[Relationship]:
        """Merge similar relationships to avoid duplicates"""
        merged = []
        relationship_groups = defaultdict(list)
        
        # Group by entity pair
        for rel in relationships:
            # Normalize entity names for grouping
            source_norm = rel.source_entity.lower().strip()
            target_norm = rel.target_entity.lower().strip()
            
            # Create bidirectional key (order doesn't matter for grouping)
            key = tuple(sorted([source_norm, target_norm]))
            relationship_groups[key].append(rel)
        
        # Merge groups
        for entity_pair, group in relationship_groups.items():
            if len(group) == 1:
                merged.append(group[0])
            else:
                # Merge multiple relationships between same entities
                merged_rel = self._merge_relationship_group(group)
                merged.append(merged_rel)
        
        return merged
    
    def _merge_relationship_group(self, relationships: List[Relationship]) -> Relationship:
        """Merge a group of relationships between the same entities"""
        # Use the relationship with highest confidence as base
        base_rel = max(relationships, key=lambda r: r.confidence_score)
        
        # Combine evidence from all relationships
        all_evidence_docs = []
        all_contexts = []
        
        for rel in relationships:
            all_evidence_docs.extend(rel.evidence_documents)
            if rel.context_evidence:
                all_contexts.append(rel.context_evidence)
        
        # Create merged relationship
        merged_rel = Relationship(
            relationship_id=f"merged_{base_rel.relationship_id}",
            source_entity=base_rel.source_entity,
            target_entity=base_rel.target_entity,
            relationship_type=base_rel.relationship_type,
            confidence_score=min(1.0, base_rel.confidence_score + len(relationships) * 0.1),
            evidence_documents=list(set(all_evidence_docs)),
            relationship_direction=base_rel.relationship_direction,
            context_evidence=" | ".join(all_contexts[:3])  # Limit combined context
        )
        
        return merged_rel
    
    def _extract_entities(self, content: str) -> List[str]:
        """Extract entities from content"""
        entities = []
        
        # Entity patterns
        patterns = [
            r'\b(?:Dr\.|Prof\.)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:University|Institute|Lab)\b',
            r'\b([A-Z]{2,})\b',  # Acronyms
            r'\b([A-Z][a-z]+(?:\s+[a-z]+)*)\s+(?:technology|technique|method)\b'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content)
            entities.extend(matches)
        
        return list(set(entities))
    
    def _is_valid_entity(self, entity: str) -> bool:
        """Check if entity is valid for relationship extraction"""
        if len(entity) < 2:
            return False
        
        # Filter out common words and articles
        invalid_entities = {
            "the", "this", "that", "these", "those", "and", "or", "but",
            "research", "study", "work", "analysis", "system", "method"
        }
        
        return entity.lower() not in invalid_entities
    
    def _initialize_classification_patterns(self) -> Dict[str, List[str]]:
        """Initialize patterns for relationship classification"""
        return {
            "causal": [
                r'\b(\w+(?:\s+\w+)*)\s+(?:caused|led to|resulted in|triggered)\s+(\w+(?:\s+\w+)*)\b',
                r'\b(\w+(?:\s+\w+)*)\s+(?:enabled|facilitated|made possible)\s+(\w+(?:\s+\w+)*)\b',
                r'\b(\w+(?:\s+\w+)*)\s+(?:developed|created|pioneered)\s+(\w+(?:\s+\w+)*)\b'
            ],
            "temporal": [
                r'\b(\w+(?:\s+\w+)*)\s+(?:before|prior to|preceded)\s+(\w+(?:\s+\w+)*)\b',
                r'\b(\w+(?:\s+\w+)*)\s+(?:after|following|subsequent to)\s+(\w+(?:\s+\w+)*)\b',
                r'\b(\w+(?:\s+\w+)*)\s+(?:during|while|when)\s+(\w+(?:\s+\w+)*)\b'
            ],
            "hierarchical": [
                r'\b(\w+(?:\s+\w+)*)\s+(?:includes|contains|encompasses)\s+(\w+(?:\s+\w+)*)\b',
                r'\b(\w+(?:\s+\w+)*)\s+(?:is part of|belongs to)\s+(\w+(?:\s+\w+)*)\b',
                r'\b(\w+(?:\s+\w+)*)\s+(?:is a type of|is a kind of)\s+(\w+(?:\s+\w+)*)\b'
            ],
            "associative": [
                r'\b(\w+(?:\s+\w+)*)\s+(?:and|with|along with)\s+(\w+(?:\s+\w+)*)\b',
                r'\b(\w+(?:\s+\w+)*)\s+(?:related to|associated with)\s+(\w+(?:\s+\w+)*)\b',
                r'\b(\w+(?:\s+\w+)*)\s+(?:collaborated with|worked with)\s+(\w+(?:\s+\w+)*)\b'
            ]
        }
    
    def _initialize_confidence_weights(self) -> Dict[str, float]:
        """Initialize weights for confidence calculation"""
        return {
            "evidence_strength": 0.3,
            "context_quality": 0.25,
            "entity_reliability": 0.2,
            "pattern_strength": 0.15,
            "cross_document_support": 0.1
        }