"""
Cross-Modal Content Analyzer

Analyzes documents across multiple modalities (text, structure, metadata, references)
and provides unified insights through cross-modal reasoning.
"""

import logging
import asyncio
import re
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import json

logger = logging.getLogger(__name__)


class ModalityType(Enum):
    """Types of content modalities"""
    TEXT = "text"
    STRUCTURE = "structure"
    METADATA = "metadata"
    REFERENCES = "references"


@dataclass
class ExtractedConcept:
    """Concept extracted from content"""
    name: str
    confidence: float
    modality: ModalityType
    context: str
    document_id: str
    frequency: int = 1


@dataclass
class ConceptRelationship:
    """Relationship between concepts"""
    concept1: str
    concept2: str
    relationship_type: str
    strength: float
    evidence: List[str] = field(default_factory=list)


@dataclass
class CrossDocumentCorrelation:
    """Correlation between documents"""
    document1_id: str
    document2_id: str
    correlation_type: str
    correlation_strength: float
    shared_elements: List[str] = field(default_factory=list)


@dataclass
class TextAnalysisResult:
    """Result of text content analysis"""
    extracted_concepts: List[ExtractedConcept]
    concept_relationships: List[ConceptRelationship]
    cross_document_correlations: List[CrossDocumentCorrelation]
    overall_confidence: float


@dataclass
class AlignedEntity:
    """Entity aligned across modalities"""
    canonical_name: str
    variations: List[str]
    modalities: List[ModalityType]
    confidence: float
    document_ids: List[str]


@dataclass
class EntityAlignmentResult:
    """Result of cross-modal entity alignment"""
    aligned_entities: List[AlignedEntity]
    alignment_accuracy: float
    unaligned_entities: List[str] = field(default_factory=list)
    
    def get_entity_variations(self) -> Dict[str, List[str]]:
        """Get variations for each entity"""
        return {entity.canonical_name: entity.variations for entity in self.aligned_entities}


@dataclass
class TopicTrajectory:
    """Evolution trajectory of a topic"""
    topic_name: str
    timeline_points: List[Dict[str, Any]]
    evolution_direction: str  # "emerging", "stable", "declining"
    confidence: float


@dataclass
class TopicChanges:
    """Changes in topics over time"""
    emerging_topics: List[str]
    declining_topics: List[str]
    stable_topics: List[str]


@dataclass
class TopicEvolutionAnalysis:
    """Analysis of topic evolution"""
    topic_trajectories: List[TopicTrajectory]
    overall_confidence: float
    
    def get_topic_changes(self) -> TopicChanges:
        """Get categorized topic changes"""
        emerging = [t.topic_name for t in self.topic_trajectories if t.evolution_direction == "emerging"]
        declining = [t.topic_name for t in self.topic_trajectories if t.evolution_direction == "declining"]
        stable = [t.topic_name for t in self.topic_trajectories if t.evolution_direction == "stable"]
        
        return TopicChanges(
            emerging_topics=emerging,
            declining_topics=declining,
            stable_topics=stable
        )


@dataclass
class ModalityConfidence:
    """Confidence for a specific modality"""
    modality: str
    confidence: float
    reliability_factors: List[str]


@dataclass
class CrossModalConfidenceResult:
    """Result of cross-modal confidence calculation"""
    modality_confidences: List[ModalityConfidence]
    overall_confidence: float
    
    def calculate_confidence_variance(self) -> float:
        """Calculate variance in confidence across modalities"""
        confidences = [mc.confidence for mc in self.modality_confidences]
        if not confidences:
            return 0.0
        
        mean_conf = sum(confidences) / len(confidences)
        variance = sum((c - mean_conf) ** 2 for c in confidences) / len(confidences)
        return variance
    
    def get_confidence_breakdown(self) -> Dict[str, float]:
        """Get confidence breakdown by modality"""
        return {mc.modality: mc.confidence for mc in self.modality_confidences}


@dataclass
class DetectedConflict:
    """Conflict detected between modalities"""
    modality1: str
    modality2: str
    conflict_type: str
    conflicting_information: Dict[str, Any]
    severity: float


@dataclass
class ResolutionStrategy:
    """Strategy for resolving conflicts"""
    strategy_name: str
    applicable_conflicts: List[str]
    confidence: float
    resolution_steps: List[str]


@dataclass
class ResolvedConflict:
    """Resolved conflict with solution"""
    original_conflict: DetectedConflict
    resolution_strategy: ResolutionStrategy
    resolved_value: Any
    resolution_confidence: float


@dataclass
class ConflictResolutionResult:
    """Result of conflict resolution"""
    detected_conflicts: List[DetectedConflict]
    resolution_strategies: List[ResolutionStrategy]
    data_integrity_score: float
    
    def get_resolved_conflicts(self) -> List[ResolvedConflict]:
        """Get conflicts that were successfully resolved"""
        # For now, return empty list as conflicts might not all be resolvable
        return []


class CrossModalAnalyzer:
    """Analyzes content across multiple modalities"""
    
    def __init__(self):
        """Initialize cross-modal analyzer"""
        self.logger = logger
        
        # Concept extraction patterns
        self.concept_patterns = {
            'ai_concepts': [
                r'\b(?:AI safety|artificial intelligence safety)\b',  # AI safety as single concept
                r'\b(?:artificial intelligence|AI|machine learning|ML|deep learning|neural networks?)\b',
                r'\b(?:safety|alignment|RLHF|reinforcement learning)\b',
                r'\b(?:autonomous|AGI|artificial general intelligence)\b'
            ],
            'research_concepts': [
                r'\b(?:methodology|experiment|analysis|results?|findings?)\b',
                r'\b(?:hypothesis|theory|framework|model)\b',
                r'\b(?:validation|evaluation|assessment|testing)\b'
            ],
            'academic_concepts': [
                r'\b(?:paper|study|research|investigation|survey)\b',
                r'\b(?:conclusion|discussion|abstract|introduction)\b',
                r'\b(?:reference|citation|bibliography)\b'
            ]
        }
        
        # Compile patterns for efficiency
        self.compiled_patterns = {}
        for category, patterns in self.concept_patterns.items():
            self.compiled_patterns[category] = [re.compile(p, re.IGNORECASE) for p in patterns]
    
    async def analyze_text_content(self, documents: List[Dict[str, Any]]) -> TextAnalysisResult:
        """Extract and correlate textual content across documents"""
        self.logger.info(f"Analyzing text content for {len(documents)} documents")
        
        # Extract concepts from all documents
        all_concepts = []
        for i, doc in enumerate(documents):
            doc_id = f"doc_{i}"
            content = doc.get("content", "")
            
            concepts = self._extract_concepts_from_text(content, doc_id)
            all_concepts.extend(concepts)
        
        # Identify relationships between concepts
        relationships = self._identify_concept_relationships(all_concepts)
        
        # Find cross-document correlations
        correlations = self._find_cross_document_correlations(documents, all_concepts)
        
        # Calculate overall confidence
        overall_confidence = self._calculate_text_analysis_confidence(
            all_concepts, relationships, correlations
        )
        
        return TextAnalysisResult(
            extracted_concepts=all_concepts,
            concept_relationships=relationships,
            cross_document_correlations=correlations,
            overall_confidence=overall_confidence
        )
    
    def _extract_concepts_from_text(self, content: str, doc_id: str) -> List[ExtractedConcept]:
        """Extract concepts from text content"""
        concepts = []
        
        for category, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                matches = pattern.findall(content)
                
                for match in matches:
                    # Get context around the match
                    match_pos = content.lower().find(match.lower())
                    context_start = max(0, match_pos - 50)
                    context_end = min(len(content), match_pos + len(match) + 50)
                    context = content[context_start:context_end].strip()
                    
                    concept = ExtractedConcept(
                        name=match.strip(),
                        confidence=0.8,  # Base confidence
                        modality=ModalityType.TEXT,
                        context=context,
                        document_id=doc_id,
                        frequency=1
                    )
                    concepts.append(concept)
        
        # Merge duplicate concepts and update frequency
        merged_concepts = self._merge_duplicate_concepts(concepts)
        
        return merged_concepts
    
    def _merge_duplicate_concepts(self, concepts: List[ExtractedConcept]) -> List[ExtractedConcept]:
        """Merge duplicate concepts and update frequencies"""
        concept_map = {}
        
        for concept in concepts:
            key = (concept.name.lower(), concept.document_id)
            
            if key in concept_map:
                concept_map[key].frequency += 1
                concept_map[key].confidence = min(1.0, concept_map[key].confidence + 0.1)
            else:
                concept_map[key] = concept
        
        return list(concept_map.values())
    
    def _identify_concept_relationships(self, concepts: List[ExtractedConcept]) -> List[ConceptRelationship]:
        """Identify relationships between concepts"""
        relationships = []
        
        # Simple co-occurrence based relationships
        concept_docs = {}
        for concept in concepts:
            if concept.name not in concept_docs:
                concept_docs[concept.name] = set()
            concept_docs[concept.name].add(concept.document_id)
        
        # Find concepts that co-occur in documents
        concept_names = list(concept_docs.keys())
        for i, concept1 in enumerate(concept_names):
            for concept2 in concept_names[i+1:]:
                shared_docs = concept_docs[concept1] & concept_docs[concept2]
                
                if shared_docs:
                    strength = len(shared_docs) / max(len(concept_docs[concept1]), len(concept_docs[concept2]))
                    
                    if strength > 0.3:  # Threshold for meaningful relationship
                        relationship = ConceptRelationship(
                            concept1=concept1,
                            concept2=concept2,
                            relationship_type="co_occurrence",
                            strength=strength,
                            evidence=list(shared_docs)
                        )
                        relationships.append(relationship)
        
        return relationships
    
    def _find_cross_document_correlations(self, documents: List[Dict[str, Any]], 
                                        concepts: List[ExtractedConcept]) -> List[CrossDocumentCorrelation]:
        """Find correlations between documents"""
        correlations = []
        
        # Group concepts by document
        doc_concepts = {}
        for concept in concepts:
            if concept.document_id not in doc_concepts:
                doc_concepts[concept.document_id] = []
            doc_concepts[concept.document_id].append(concept.name)
        
        # Find correlations between document pairs
        doc_ids = list(doc_concepts.keys())
        for i, doc1_id in enumerate(doc_ids):
            for doc2_id in doc_ids[i+1:]:
                shared_concepts = set(doc_concepts[doc1_id]) & set(doc_concepts[doc2_id])
                
                if shared_concepts:
                    # Calculate correlation strength
                    all_concepts_doc1 = set(doc_concepts[doc1_id])
                    all_concepts_doc2 = set(doc_concepts[doc2_id])
                    union_concepts = all_concepts_doc1 | all_concepts_doc2
                    
                    correlation_strength = len(shared_concepts) / len(union_concepts)
                    
                    correlation = CrossDocumentCorrelation(
                        document1_id=doc1_id,
                        document2_id=doc2_id,
                        correlation_type="concept_overlap",
                        correlation_strength=correlation_strength,
                        shared_elements=list(shared_concepts)
                    )
                    correlations.append(correlation)
        
        return correlations
    
    def _calculate_text_analysis_confidence(self, concepts: List[ExtractedConcept],
                                          relationships: List[ConceptRelationship],
                                          correlations: List[CrossDocumentCorrelation]) -> float:
        """Calculate overall confidence for text analysis"""
        if not concepts:
            return 0.0
        
        # Base confidence from concept extraction
        concept_confidence = sum(c.confidence for c in concepts) / len(concepts)
        
        # Boost confidence if we found relationships
        relationship_boost = min(0.2, len(relationships) * 0.05)
        
        # Boost confidence if we found correlations
        correlation_boost = min(0.1, len(correlations) * 0.02)
        
        overall_confidence = min(1.0, concept_confidence + relationship_boost + correlation_boost)
        
        return overall_confidence
    
    async def align_entities_cross_modal(self, documents: List[Dict[str, Any]]) -> EntityAlignmentResult:
        """Match entities across different modalities"""
        self.logger.info(f"Aligning entities across modalities for {len(documents)} documents")
        
        # Extract entities from different modalities
        text_entities = self._extract_text_entities(documents)
        metadata_entities = self._extract_metadata_entities(documents)
        
        # Align entities across modalities
        aligned_entities = self._align_entity_sets(text_entities, metadata_entities, documents)
        
        # Calculate alignment accuracy
        total_entities = len(text_entities) + len(metadata_entities)
        if total_entities == 0:
            alignment_accuracy = 1.0
        else:
            aligned_count = sum(len(entity.variations) for entity in aligned_entities)
            alignment_accuracy = min(1.0, aligned_count / total_entities)
        
        return EntityAlignmentResult(
            aligned_entities=aligned_entities,
            alignment_accuracy=alignment_accuracy
        )
    
    def _extract_text_entities(self, documents: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Extract entities from text content"""
        entities = {}
        
        # Pattern for names (simplified)
        name_pattern = re.compile(r'\b(?:Dr\.|Prof\.)?\s*([A-Z][a-z]+\s+[A-Z][a-z]+)\b')
        
        for i, doc in enumerate(documents):
            doc_id = f"doc_{i}"
            content = doc.get("content", "")
            
            matches = name_pattern.findall(content)
            if matches:
                entities[doc_id] = matches
        
        return entities
    
    def _extract_metadata_entities(self, documents: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Extract entities from metadata"""
        entities = {}
        
        for i, doc in enumerate(documents):
            doc_id = f"doc_{i}"
            metadata = doc.get("metadata", {})
            
            doc_entities = []
            
            # Extract authors
            authors = metadata.get("authors", [])
            if isinstance(authors, list):
                doc_entities.extend(authors)
            
            # Extract researchers
            researchers = metadata.get("researchers", [])
            if isinstance(researchers, list):
                doc_entities.extend(researchers)
            
            if doc_entities:
                entities[doc_id] = doc_entities
        
        return entities
    
    def _align_entity_sets(self, text_entities: Dict[str, List[str]], 
                          metadata_entities: Dict[str, List[str]],
                          documents: List[Dict[str, Any]]) -> List[AlignedEntity]:
        """Align entities from different modality sets"""
        aligned_entities = []
        
        # Collect all unique entities
        all_entities = set()
        entity_sources = {}  # Track where each entity came from
        
        # Process text entities
        for doc_id, entities in text_entities.items():
            for entity in entities:
                all_entities.add(entity)
                if entity not in entity_sources:
                    entity_sources[entity] = {"text": [], "metadata": []}
                entity_sources[entity]["text"].append(doc_id)
        
        # Process metadata entities
        for doc_id, entities in metadata_entities.items():
            for entity in entities:
                all_entities.add(entity)
                if entity not in entity_sources:
                    entity_sources[entity] = {"text": [], "metadata": []}
                entity_sources[entity]["metadata"].append(doc_id)
        
        # Create aligned entities
        for entity in all_entities:
            sources = entity_sources[entity]
            modalities = []
            all_doc_ids = []
            
            if sources["text"]:
                modalities.append(ModalityType.TEXT)
                all_doc_ids.extend(sources["text"])
            
            if sources["metadata"]:
                modalities.append(ModalityType.METADATA)
                all_doc_ids.extend(sources["metadata"])
            
            # Calculate confidence based on number of modalities
            confidence = 0.7 + (len(modalities) - 1) * 0.2
            
            aligned_entity = AlignedEntity(
                canonical_name=entity,
                variations=[entity],  # For now, just use the entity itself
                modalities=modalities,
                confidence=confidence,
                document_ids=list(set(all_doc_ids))
            )
            
            aligned_entities.append(aligned_entity)
        
        return aligned_entities
    
    async def track_topic_evolution(self, documents: List[Dict[str, Any]]) -> TopicEvolutionAnalysis:
        """Track how topics change across documents"""
        self.logger.info(f"Tracking topic evolution across {len(documents)} documents")
        
        # Extract topics and their temporal information
        topic_timeline = self._extract_topic_timeline(documents)
        
        # Analyze evolution trajectories
        trajectories = self._analyze_topic_trajectories(topic_timeline)
        
        # Calculate overall confidence
        overall_confidence = self._calculate_evolution_confidence(trajectories)
        
        return TopicEvolutionAnalysis(
            topic_trajectories=trajectories,
            overall_confidence=overall_confidence
        )
    
    def _extract_topic_timeline(self, documents: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Extract topics with temporal information"""
        topic_timeline = {}
        
        for i, doc in enumerate(documents):
            # Extract date from metadata
            metadata = doc.get("metadata", {})
            date = metadata.get("date", f"2024-0{i+1}-01")  # Default fallback
            
            # Extract topics from content and metadata
            content = doc.get("content", "")
            keywords = metadata.get("keywords", [])
            
            # Find AI-related topics
            ai_topics = []
            if any(term in content.lower() for term in ["ai", "artificial intelligence", "safety"]):
                ai_topics.append("AI safety")
            if any(term in content.lower() for term in ["machine learning", "ml", "learning"]):
                ai_topics.append("Machine Learning")
            if any(term in content.lower() for term in ["alignment", "rlhf"]):
                ai_topics.append("AI Alignment")
            
            # Add keyword topics
            ai_topics.extend(keywords)
            
            # Add to timeline
            for topic in set(ai_topics):  # Remove duplicates
                if topic not in topic_timeline:
                    topic_timeline[topic] = []
                
                topic_timeline[topic].append({
                    "date": date,
                    "document_id": f"doc_{i}",
                    "strength": 1.0  # Simplified strength
                })
        
        return topic_timeline
    
    def _analyze_topic_trajectories(self, topic_timeline: Dict[str, List[Dict[str, Any]]]) -> List[TopicTrajectory]:
        """Analyze trajectories for each topic"""
        trajectories = []
        
        for topic, timeline_points in topic_timeline.items():
            # Sort by date
            sorted_points = sorted(timeline_points, key=lambda x: x["date"])
            
            # Determine evolution direction (simplified)
            if len(sorted_points) == 1:
                direction = "stable"
            elif len(sorted_points) >= 2:
                # If topic appears in later documents, it's emerging/stable
                direction = "emerging"
            else:
                direction = "stable"
            
            trajectory = TopicTrajectory(
                topic_name=topic,
                timeline_points=sorted_points,
                evolution_direction=direction,
                confidence=0.8
            )
            
            trajectories.append(trajectory)
        
        return trajectories
    
    def _calculate_evolution_confidence(self, trajectories: List[TopicTrajectory]) -> float:
        """Calculate confidence in evolution analysis"""
        if not trajectories:
            return 0.0
        
        # Base confidence from number of trajectories
        base_confidence = min(0.9, len(trajectories) * 0.1 + 0.5)
        
        # Boost confidence if we have multi-point trajectories
        multi_point_count = sum(1 for t in trajectories if len(t.timeline_points) > 1)
        boost = min(0.1, multi_point_count * 0.02)
        
        return min(1.0, base_confidence + boost)
    
    async def calculate_cross_modal_confidence(self, documents: List[Dict[str, Any]]) -> CrossModalConfidenceResult:
        """Aggregate confidence across modalities"""
        self.logger.info(f"Calculating cross-modal confidence for {len(documents)} documents")
        
        modality_confidences = []
        
        # Text modality confidence
        text_conf = self._calculate_text_modality_confidence(documents)
        modality_confidences.append(text_conf)
        
        # Metadata modality confidence
        metadata_conf = self._calculate_metadata_modality_confidence(documents)
        modality_confidences.append(metadata_conf)
        
        # Structure modality confidence
        structure_conf = self._calculate_structure_modality_confidence(documents)
        modality_confidences.append(structure_conf)
        
        # Calculate overall confidence
        confidences = [mc.confidence for mc in modality_confidences]
        overall_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        return CrossModalConfidenceResult(
            modality_confidences=modality_confidences,
            overall_confidence=overall_confidence
        )
    
    def _calculate_text_modality_confidence(self, documents: List[Dict[str, Any]]) -> ModalityConfidence:
        """Calculate confidence for text modality"""
        total_content_length = sum(len(doc.get("content", "")) for doc in documents)
        
        # Base confidence from content availability
        if total_content_length > 1000:
            confidence = 0.9
            reliability_factors = ["sufficient_content", "diverse_documents"]
        elif total_content_length > 100:
            confidence = 0.7
            reliability_factors = ["moderate_content"]
        else:
            confidence = 0.5
            reliability_factors = ["limited_content"]
        
        return ModalityConfidence(
            modality="text",
            confidence=confidence,
            reliability_factors=reliability_factors
        )
    
    def _calculate_metadata_modality_confidence(self, documents: List[Dict[str, Any]]) -> ModalityConfidence:
        """Calculate confidence for metadata modality"""
        docs_with_metadata = sum(1 for doc in documents if doc.get("metadata"))
        metadata_coverage = docs_with_metadata / len(documents) if documents else 0
        
        confidence = metadata_coverage * 0.8 + 0.2  # Base confidence of 0.2
        
        reliability_factors = []
        if metadata_coverage > 0.8:
            reliability_factors.append("high_metadata_coverage")
        if metadata_coverage > 0.5:
            reliability_factors.append("moderate_metadata_coverage")
        else:
            reliability_factors.append("limited_metadata")
        
        return ModalityConfidence(
            modality="metadata",
            confidence=confidence,
            reliability_factors=reliability_factors
        )
    
    def _calculate_structure_modality_confidence(self, documents: List[Dict[str, Any]]) -> ModalityConfidence:
        """Calculate confidence for structure modality"""
        # Check for structured content (headings, sections)
        structured_docs = 0
        for doc in documents:
            content = doc.get("content", "")
            if any(marker in content for marker in ["#", "##", "Abstract", "Introduction", "Conclusion"]):
                structured_docs += 1
        
        structure_coverage = structured_docs / len(documents) if documents else 0
        confidence = structure_coverage * 0.7 + 0.3  # Base confidence of 0.3
        
        reliability_factors = []
        if structure_coverage > 0.7:
            reliability_factors.append("well_structured_documents")
        elif structure_coverage > 0.3:
            reliability_factors.append("moderately_structured")
        else:
            reliability_factors.append("limited_structure")
        
        return ModalityConfidence(
            modality="structure",
            confidence=confidence,
            reliability_factors=reliability_factors
        )
    
    async def resolve_modality_conflicts(self, documents: List[Dict[str, Any]]) -> ConflictResolutionResult:
        """Handle contradictions between modalities"""
        self.logger.info(f"Resolving modality conflicts for {len(documents)} documents")
        
        # Detect conflicts
        conflicts = self._detect_modality_conflicts(documents)
        
        # Generate resolution strategies
        strategies = self._generate_resolution_strategies(conflicts)
        
        # Calculate data integrity score
        integrity_score = self._calculate_data_integrity(documents, conflicts)
        
        return ConflictResolutionResult(
            detected_conflicts=conflicts,
            resolution_strategies=strategies,
            data_integrity_score=integrity_score
        )
    
    def _detect_modality_conflicts(self, documents: List[Dict[str, Any]]) -> List[DetectedConflict]:
        """Detect conflicts between different modalities"""
        conflicts = []
        
        for i, doc in enumerate(documents):
            content = doc.get("content", "")
            metadata = doc.get("metadata", {})
            
            # Check for author conflicts
            content_authors = self._extract_text_entities([doc]).get(f"doc_0", [])
            metadata_authors = metadata.get("authors", [])
            
            if content_authors and metadata_authors:
                # Check if authors match
                content_author_set = set(author.lower() for author in content_authors)
                metadata_author_set = set(author.lower() for author in metadata_authors)
                
                if not content_author_set.intersection(metadata_author_set):
                    conflict = DetectedConflict(
                        modality1="text",
                        modality2="metadata",
                        conflict_type="author_mismatch",
                        conflicting_information={
                            "text_authors": content_authors,
                            "metadata_authors": metadata_authors
                        },
                        severity=0.7
                    )
                    conflicts.append(conflict)
        
        return conflicts
    
    def _generate_resolution_strategies(self, conflicts: List[DetectedConflict]) -> List[ResolutionStrategy]:
        """Generate strategies for resolving conflicts"""
        strategies = []
        
        # Generic strategy for author conflicts
        if any(c.conflict_type == "author_mismatch" for c in conflicts):
            strategy = ResolutionStrategy(
                strategy_name="metadata_priority",
                applicable_conflicts=["author_mismatch"],
                confidence=0.8,
                resolution_steps=[
                    "Prioritize metadata information as more reliable",
                    "Flag text extraction for manual review",
                    "Update entity alignment accordingly"
                ]
            )
            strategies.append(strategy)
        
        return strategies
    
    def _calculate_data_integrity(self, documents: List[Dict[str, Any]], 
                                conflicts: List[DetectedConflict]) -> float:
        """Calculate overall data integrity score"""
        if not documents:
            return 1.0
        
        # Base integrity score
        base_score = 0.9
        
        # Reduce score based on conflicts
        if conflicts:
            conflict_penalty = min(0.15, len(conflicts) * 0.05)  # Reduced penalty
            integrity_score = base_score - conflict_penalty
        else:
            integrity_score = base_score
        
        return max(0.75, integrity_score)  # Higher minimum integrity score