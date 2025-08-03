#!/usr/bin/env python3
"""
Entity Linking and Deduplication System

Provides comprehensive entity linking and deduplication across documents,
including name variation handling, disambiguation, cross-document resolution,
and consolidated entity profile creation for research knowledge graphs.
"""

import logging
import asyncio
import time
import hashlib
import json
from typing import Dict, List, Optional, Any, Tuple, Set, Union, Callable
from dataclasses import dataclass, field, asdict
from datetime import datetime
from collections import defaultdict, Counter
from pathlib import Path
from abc import ABC, abstractmethod
from enum import Enum
import re
import string
from difflib import SequenceMatcher
import statistics

# NLP and similarity libraries
try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
    from nltk.stem import WordNetLemmatizer
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.cluster import DBSCAN, AgglomerativeClustering
    SIMILARITY_AVAILABLE = True
except ImportError:
    SIMILARITY_AVAILABLE = False

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

try:
    from fuzzywuzzy import fuzz, process
    FUZZY_AVAILABLE = True
except ImportError:
    FUZZY_AVAILABLE = False

logger = logging.getLogger(__name__)


class EntityType(Enum):
    """Standard entity types"""
    PERSON = "PERSON"
    ORGANIZATION = "ORG"
    LOCATION = "LOC"
    DATE = "DATE"
    TIME = "TIME"
    MONEY = "MONEY"
    PERCENT = "PERCENT"
    FACILITY = "FACILITY"
    GPE = "GPE"  # Geopolitical entity
    PRODUCT = "PRODUCT"
    EVENT = "EVENT"
    WORK_OF_ART = "WORK_OF_ART"
    LAW = "LAW"
    LANGUAGE = "LANGUAGE"
    NORP = "NORP"  # Nationalities, religious/political groups
    CARDINAL = "CARDINAL"  # Numerals that don't fall under other types
    ORDINAL = "ORDINAL"
    QUANTITY = "QUANTITY"
    MISC = "MISC"
    UNKNOWN = "UNKNOWN"


class LinkingConfidence(Enum):
    """Confidence levels for entity linking"""
    CERTAIN = "certain"        # > 0.9
    HIGH = "high"             # 0.8 - 0.9
    MEDIUM = "medium"         # 0.6 - 0.8
    LOW = "low"               # 0.4 - 0.6
    UNCERTAIN = "uncertain"   # < 0.4


@dataclass
class EntityMention:
    """Single mention of an entity in text"""
    mention_id: str
    text: str
    normalized_text: str
    document_id: str
    start_position: int
    end_position: int
    entity_type: EntityType
    confidence: float
    context: str = ""  # Surrounding text context
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.mention_id:
            self.mention_id = self._generate_mention_id()
    
    def _generate_mention_id(self) -> str:
        """Generate unique mention ID"""
        content = f"{self.document_id}_{self.start_position}_{self.end_position}_{self.text}"
        return hashlib.md5(content.encode()).hexdigest()[:12]


@dataclass
class EntityProfile:
    """Consolidated entity profile across all mentions"""
    entity_id: str
    canonical_name: str
    entity_type: EntityType
    alternative_names: Set[str] = field(default_factory=set)
    mentions: List[EntityMention] = field(default_factory=list)
    
    # Aggregated information
    total_mentions: int = 0
    document_frequency: int = 0  # Number of documents containing this entity
    documents: Set[str] = field(default_factory=set)
    contexts: List[str] = field(default_factory=list)
    
    # Quality metrics
    name_consistency_score: float = 0.0
    context_coherence_score: float = 0.0
    overall_confidence: float = 0.0
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    attributes: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.entity_id:
            self.entity_id = self._generate_entity_id()
    
    def _generate_entity_id(self) -> str:
        """Generate unique entity ID"""
        content = f"{self.canonical_name}_{self.entity_type.value}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def add_mention(self, mention: EntityMention):
        """Add a mention to this entity profile"""
        self.mentions.append(mention)
        self.alternative_names.add(mention.normalized_text)
        self.documents.add(mention.document_id)
        if mention.context:
            self.contexts.append(mention.context)
        
        # Update aggregated metrics
        self.total_mentions = len(self.mentions)
        self.document_frequency = len(self.documents)
        self.updated_at = datetime.now()
    
    def get_primary_context(self, max_length: int = 200) -> str:
        """Get most representative context"""
        if not self.contexts:
            return ""
        
        # Find the longest context (likely most informative)
        longest_context = max(self.contexts, key=len)
        
        if len(longest_context) <= max_length:
            return longest_context
        else:
            # Truncate while preserving word boundaries
            truncated = longest_context[:max_length]
            last_space = truncated.rfind(' ')
            if last_space > max_length * 0.8:  # If we can preserve most of the text
                return truncated[:last_space] + "..."
            else:
                return truncated + "..."


@dataclass
class LinkingResult:
    """Result of entity linking process"""
    entity_profiles: List[EntityProfile] = field(default_factory=list)
    total_mentions: int = 0
    total_entities: int = 0
    duplicate_groups: List[List[str]] = field(default_factory=list)  # Groups of duplicate entity IDs
    
    # Quality metrics
    average_confidence: float = 0.0
    linking_precision: float = 0.0
    linking_recall: float = 0.0
    
    # Processing metadata
    processing_time: float = 0.0
    method_used: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    def get_entity_by_id(self, entity_id: str) -> Optional[EntityProfile]:
        """Get entity profile by ID"""
        for entity in self.entity_profiles:
            if entity.entity_id == entity_id:
                return entity
        return None
    
    def get_entities_by_type(self, entity_type: EntityType) -> List[EntityProfile]:
        """Get all entities of specific type"""
        return [e for e in self.entity_profiles if e.entity_type == entity_type]


class SimilarityCalculator(ABC):
    """Abstract base for similarity calculation methods"""
    
    @abstractmethod
    def calculate_similarity(self, text1: str, text2: str, **kwargs) -> float:
        """Calculate similarity between two text strings"""
        pass
    
    @abstractmethod
    def get_calculator_info(self) -> Dict[str, Any]:
        """Get information about this calculator"""
        pass


class StringSimilarityCalculator(SimilarityCalculator):
    """String-based similarity calculations"""
    
    def __init__(self):
        self.name = "StringSimilarityCalculator"
        
        # Initialize components
        self.lemmatizer = None
        if NLTK_AVAILABLE:
            try:
                self.lemmatizer = WordNetLemmatizer()
                # Ensure NLTK data is available
                import nltk
                nltk.download('wordnet', quiet=True)
                nltk.download('stopwords', quiet=True)
            except Exception as e:
                logger.warning(f"NLTK setup failed: {e}")
    
    def calculate_similarity(self, text1: str, text2: str, **kwargs) -> float:
        """Calculate string similarity using multiple methods"""
        if not text1 or not text2:
            return 0.0
        
        # Normalize texts
        norm_text1 = self._normalize_text(text1)
        norm_text2 = self._normalize_text(text2)
        
        if norm_text1 == norm_text2:
            return 1.0
        
        # Calculate multiple similarity metrics
        similarities = []
        
        # 1. Exact string similarity (after normalization)
        if norm_text1.lower() == norm_text2.lower():
            similarities.append(1.0)
        
        # 2. Jaccard similarity (word overlap)
        jaccard_sim = self._jaccard_similarity(norm_text1, norm_text2)
        similarities.append(jaccard_sim)
        
        # 3. Edit distance similarity
        edit_sim = self._edit_distance_similarity(norm_text1, norm_text2)
        similarities.append(edit_sim)
        
        # 4. Fuzzy string matching if available
        if FUZZY_AVAILABLE:
            fuzzy_sim = fuzz.ratio(norm_text1.lower(), norm_text2.lower()) / 100.0
            similarities.append(fuzzy_sim)
        
        # 5. Token-based similarity
        token_sim = self._token_similarity(norm_text1, norm_text2)
        similarities.append(token_sim)
        
        # Return weighted average
        return statistics.mean(similarities)
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for comparison"""
        # Basic normalization
        normalized = text.strip()
        
        # Remove extra whitespace
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # Remove common prefixes/suffixes that don't affect identity
        prefixes = ['Mr.', 'Mrs.', 'Ms.', 'Dr.', 'Prof.', 'The']
        suffixes = ['Inc.', 'Corp.', 'Ltd.', 'LLC', 'Co.']
        
        words = normalized.split()
        
        # Remove prefixes
        if words and words[0] in prefixes:
            words = words[1:]
        
        # Remove suffixes
        if words and words[-1] in suffixes:
            words = words[:-1]
        
        return ' '.join(words).strip()
    
    def _jaccard_similarity(self, text1: str, text2: str) -> float:
        """Calculate Jaccard similarity between word sets"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 and not words2:
            return 1.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _edit_distance_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity based on edit distance"""
        if not text1 and not text2:
            return 1.0
        
        max_len = max(len(text1), len(text2))
        if max_len == 0:
            return 1.0
        
        # Use SequenceMatcher for edit distance
        matcher = SequenceMatcher(None, text1.lower(), text2.lower())
        return matcher.ratio()
    
    def _token_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity based on token overlap"""
        if NLTK_AVAILABLE:
            try:
                tokens1 = word_tokenize(text1.lower())
                tokens2 = word_tokenize(text2.lower())
                
                # Remove stopwords
                stop_words = set(stopwords.words('english'))
                tokens1 = [t for t in tokens1 if t not in stop_words and t.isalpha()]
                tokens2 = [t for t in tokens2 if t not in stop_words and t.isalpha()]
                
                # Lemmatize if available
                if self.lemmatizer:
                    tokens1 = [self.lemmatizer.lemmatize(t) for t in tokens1]
                    tokens2 = [self.lemmatizer.lemmatize(t) for t in tokens2]
                
                # Calculate overlap
                set1, set2 = set(tokens1), set(tokens2)
                if not set1 and not set2:
                    return 1.0
                
                intersection = set1.intersection(set2)
                union = set1.union(set2)
                
                return len(intersection) / len(union) if union else 0.0
                
            except Exception:
                pass
        
        # Fallback to simple word overlap
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 and not words2:
            return 1.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def get_calculator_info(self) -> Dict[str, Any]:
        """Get calculator information"""
        return {
            "calculator_name": self.name,
            "methods": [
                "exact_match",
                "jaccard_similarity", 
                "edit_distance",
                "fuzzy_matching" if FUZZY_AVAILABLE else None,
                "token_similarity"
            ],
            "nltk_available": NLTK_AVAILABLE,
            "fuzzy_available": FUZZY_AVAILABLE
        }


class SemanticSimilarityCalculator(SimilarityCalculator):
    """Semantic similarity using embeddings"""
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.name = "SemanticSimilarityCalculator"
        self.model_name = model_name
        self.model = None
        
        if SIMILARITY_AVAILABLE:
            try:
                self.model = SentenceTransformer(model_name)
                logger.info(f"Loaded semantic similarity model: {model_name}")
            except Exception as e:
                logger.warning(f"Failed to load semantic model: {e}")
    
    def calculate_similarity(self, text1: str, text2: str, **kwargs) -> float:
        """Calculate semantic similarity using embeddings"""
        if not self.model or not text1 or not text2:
            return 0.0
        
        try:
            # Get embeddings
            embeddings = self.model.encode([text1, text2])
            
            # Calculate cosine similarity
            similarity_matrix = cosine_similarity([embeddings[0]], [embeddings[1]])
            similarity = similarity_matrix[0][0]
            
            # Ensure similarity is between 0 and 1
            return max(0.0, min(1.0, float(similarity)))
            
        except Exception as e:
            logger.warning(f"Semantic similarity calculation failed: {e}")
            return 0.0
    
    def get_calculator_info(self) -> Dict[str, Any]:
        """Get calculator information"""
        return {
            "calculator_name": self.name,
            "model_name": self.model_name,
            "model_available": self.model is not None,
            "method": "sentence_transformers_cosine_similarity"
        }


class EntityLinker:
    """Main entity linking and deduplication system"""
    
    def __init__(self, 
                 string_similarity_threshold: float = 0.8,
                 semantic_similarity_threshold: float = 0.7,
                 use_semantic_similarity: bool = True):
        
        self.string_similarity_threshold = string_similarity_threshold
        self.semantic_similarity_threshold = semantic_similarity_threshold
        self.use_semantic_similarity = use_semantic_similarity
        
        # Initialize similarity calculators
        self.string_calculator = StringSimilarityCalculator()
        self.semantic_calculator = None
        
        if use_semantic_similarity and SIMILARITY_AVAILABLE:
            self.semantic_calculator = SemanticSimilarityCalculator()
        
        # Entity storage
        self.entity_profiles = {}  # entity_id -> EntityProfile
        self.mention_to_entity = {}  # mention_id -> entity_id
        
        # Processing statistics
        self.linking_stats = {
            'total_mentions_processed': 0,
            'entities_created': 0,
            'entities_merged': 0,
            'linking_operations': 0,
            'processing_time': 0.0
        }
        
        logger.info(f"EntityLinker initialized with string_threshold={string_similarity_threshold}, semantic_threshold={semantic_similarity_threshold}")
    
    def link_mentions(self, mentions: List[EntityMention]) -> LinkingResult:
        """Link mentions across documents and create entity profiles"""
        start_time = time.time()
        
        # Reset state for new linking operation
        self.entity_profiles = {}
        self.mention_to_entity = {}
        
        if not mentions:
            return LinkingResult(
                processing_time=time.time() - start_time,
                method_used="empty_input"
            )
        
        logger.info(f"Starting entity linking for {len(mentions)} mentions")
        
        # Group mentions by entity type for efficiency
        mentions_by_type = defaultdict(list)
        for mention in mentions:
            mentions_by_type[mention.entity_type].append(mention)
        
        # Process each entity type separately
        for entity_type, type_mentions in mentions_by_type.items():
            logger.info(f"Processing {len(type_mentions)} mentions of type {entity_type.value}")
            self._link_mentions_of_type(type_mentions, entity_type)
        
        # Create result
        result = self._create_linking_result(mentions, start_time)
        
        # Update statistics
        self.linking_stats['total_mentions_processed'] += len(mentions)
        self.linking_stats['linking_operations'] += 1
        self.linking_stats['processing_time'] += result.processing_time
        
        logger.info(f"Entity linking completed: {result.total_entities} entities from {result.total_mentions} mentions")
        
        return result
    
    def _link_mentions_of_type(self, mentions: List[EntityMention], entity_type: EntityType):
        """Link mentions of the same entity type"""
        if not mentions:
            return
        
        # Initialize each mention as its own entity initially
        for mention in mentions:
            entity_id = self._create_new_entity(mention)
            self.mention_to_entity[mention.mention_id] = entity_id
        
        # Perform pairwise similarity comparison and clustering
        similarity_matrix = self._calculate_similarity_matrix(mentions)
        
        # Find clusters of similar mentions
        clusters = self._cluster_similar_mentions(mentions, similarity_matrix)
        
        # Merge mentions in the same cluster
        for cluster in clusters:
            if len(cluster) > 1:
                self._merge_mentions_into_entity(cluster)
    
    def _calculate_similarity_matrix(self, mentions: List[EntityMention]) -> np.ndarray:
        """Calculate similarity matrix between all mention pairs"""
        n = len(mentions)
        
        if SIMILARITY_AVAILABLE:
            similarity_matrix = np.zeros((n, n))
        else:
            similarity_matrix = [[0.0 for _ in range(n)] for _ in range(n)]
        
        for i in range(n):
            for j in range(i, n):
                if i == j:
                    sim = 1.0
                else:
                    sim = self._calculate_mention_similarity(mentions[i], mentions[j])
                
                if SIMILARITY_AVAILABLE:
                    similarity_matrix[i][j] = sim
                    similarity_matrix[j][i] = sim
                else:
                    similarity_matrix[i][j] = sim
                    similarity_matrix[j][i] = sim
        
        return similarity_matrix
    
    def _calculate_mention_similarity(self, mention1: EntityMention, mention2: EntityMention) -> float:
        """Calculate similarity between two mentions"""
        # Start with string similarity
        string_sim = self.string_calculator.calculate_similarity(
            mention1.normalized_text, 
            mention2.normalized_text
        )
        
        # Add semantic similarity if available
        if self.semantic_calculator and self.use_semantic_similarity:
            # Use context for better semantic understanding
            context1 = f"{mention1.normalized_text} {mention1.context}"
            context2 = f"{mention2.normalized_text} {mention2.context}"
            
            semantic_sim = self.semantic_calculator.calculate_similarity(context1, context2)
            
            # Weighted combination of string and semantic similarity
            combined_sim = (string_sim * 0.6) + (semantic_sim * 0.4)
        else:
            combined_sim = string_sim
        
        # Apply entity type consistency bonus
        if mention1.entity_type == mention2.entity_type:
            combined_sim *= 1.1  # 10% bonus for same type
        
        # Apply document co-occurrence penalty (same entity in same doc less likely)
        if mention1.document_id == mention2.document_id:
            # Check if mentions are close in position (might be the same occurrence)
            pos_diff = abs(mention1.start_position - mention2.start_position)
            if pos_diff < 50:  # Very close mentions might be duplicates
                combined_sim *= 1.2
            else:  # Same document but distant positions
                combined_sim *= 0.9
        
        return min(combined_sim, 1.0)
    
    def _cluster_similar_mentions(self, mentions: List[EntityMention], 
                                similarity_matrix: Union[np.ndarray, List[List[float]]]) -> List[List[int]]:
        """Cluster similar mentions using similarity thresholds"""
        n = len(mentions)
        
        if n <= 1:
            return [[0]] if n == 1 else []
        
        # Use DBSCAN clustering if available
        if SIMILARITY_AVAILABLE and isinstance(similarity_matrix, np.ndarray):
            try:
                # Convert similarity to distance matrix
                distance_matrix = 1.0 - similarity_matrix
                
                # Use DBSCAN for clustering
                clustering = DBSCAN(
                    metric='precomputed',
                    eps=1.0 - self.string_similarity_threshold,
                    min_samples=1
                ).fit(distance_matrix)
                
                # Group mentions by cluster labels
                clusters = defaultdict(list)
                for i, label in enumerate(clustering.labels_):
                    if label != -1:  # -1 is noise in DBSCAN
                        clusters[label].append(i)
                    else:
                        clusters[f"noise_{i}"] = [i]  # Each noise point gets its own cluster
                
                return list(clusters.values())
                
            except Exception as e:
                logger.warning(f"DBSCAN clustering failed: {e}")
        
        # Fallback: simple threshold-based clustering
        clusters = []
        assigned = [False] * n
        
        for i in range(n):
            if assigned[i]:
                continue
            
            # Start new cluster
            cluster = [i]
            assigned[i] = True
            
            # Find all similar mentions
            for j in range(i + 1, n):
                if assigned[j]:
                    continue
                
                if SIMILARITY_AVAILABLE:
                    similarity = similarity_matrix[i][j]
                else:
                    similarity = similarity_matrix[i][j]
                
                if similarity >= self.string_similarity_threshold:
                    cluster.append(j)
                    assigned[j] = True
            
            clusters.append(cluster)
        
        return clusters
    
    def _create_new_entity(self, mention: EntityMention) -> str:
        """Create new entity profile from mention"""
        entity_profile = EntityProfile(
            canonical_name=mention.normalized_text,
            entity_type=mention.entity_type
        )
        
        entity_profile.add_mention(mention)
        self.entity_profiles[entity_profile.entity_id] = entity_profile
        self.linking_stats['entities_created'] += 1
        
        return entity_profile.entity_id
    
    def _merge_mentions_into_entity(self, mention_indices: List[int]):
        """Merge multiple mentions into a single entity"""
        if len(mention_indices) <= 1:
            return
        
        # Get entity IDs for all mentions
        entity_ids = []
        for idx in mention_indices:
            mention_id = list(self.mention_to_entity.keys())[idx % len(self.mention_to_entity)]
            entity_id = self.mention_to_entity.get(mention_id)
            if entity_id and entity_id in self.entity_profiles:
                entity_ids.append(entity_id)
        
        if len(set(entity_ids)) <= 1:
            return  # Already merged or no valid entities
        
        # Choose the entity with the most mentions as the target
        entity_profiles = [self.entity_profiles[eid] for eid in set(entity_ids)]
        target_entity = max(entity_profiles, key=lambda e: e.total_mentions)
        
        # Merge other entities into the target
        for entity in entity_profiles:
            if entity.entity_id != target_entity.entity_id:
                self._merge_entities(target_entity.entity_id, entity.entity_id)
    
    def _merge_entities(self, target_entity_id: str, source_entity_id: str):
        """Merge source entity into target entity"""
        if target_entity_id == source_entity_id:
            return
        
        target_entity = self.entity_profiles.get(target_entity_id)
        source_entity = self.entity_profiles.get(source_entity_id)
        
        if not target_entity or not source_entity:
            return
        
        # Merge mentions
        for mention in source_entity.mentions:
            target_entity.add_mention(mention)
            self.mention_to_entity[mention.mention_id] = target_entity_id
        
        # Merge alternative names
        target_entity.alternative_names.update(source_entity.alternative_names)
        
        # Update canonical name if source has better name
        if (len(source_entity.canonical_name) > len(target_entity.canonical_name) and
            len(source_entity.canonical_name.split()) <= len(target_entity.canonical_name.split())):
            target_entity.canonical_name = source_entity.canonical_name
        
        # Merge attributes
        for key, value in source_entity.attributes.items():
            if key not in target_entity.attributes:
                target_entity.attributes[key] = value
        
        # Remove source entity
        del self.entity_profiles[source_entity_id]
        self.linking_stats['entities_merged'] += 1
    
    def _create_linking_result(self, mentions: List[EntityMention], start_time: float) -> LinkingResult:
        """Create final linking result"""
        result = LinkingResult(
            entity_profiles=list(self.entity_profiles.values()),
            total_mentions=len(mentions),
            total_entities=len(self.entity_profiles),
            processing_time=time.time() - start_time,
            method_used="multi_similarity_clustering"
        )
        
        # Calculate quality metrics
        if result.entity_profiles:
            confidences = []
            for entity in result.entity_profiles:
                # Calculate entity confidence based on mention consistency
                entity_confidence = self._calculate_entity_confidence(entity)
                entity.overall_confidence = entity_confidence
                confidences.append(entity_confidence)
            
            result.average_confidence = statistics.mean(confidences)
        
        # Add processing parameters
        result.parameters = {
            "string_similarity_threshold": self.string_similarity_threshold,
            "semantic_similarity_threshold": self.semantic_similarity_threshold,
            "use_semantic_similarity": self.use_semantic_similarity,
            "semantic_model_available": self.semantic_calculator is not None
        }
        
        return result
    
    def _calculate_entity_confidence(self, entity: EntityProfile) -> float:
        """Calculate confidence score for entity"""
        if not entity.mentions:
            return 0.0
        
        confidence_factors = []
        
        # Name consistency (how similar are the alternative names)
        if len(entity.alternative_names) > 1:
            name_similarities = []
            names = list(entity.alternative_names)
            
            for i in range(len(names)):
                for j in range(i + 1, len(names)):
                    sim = self.string_calculator.calculate_similarity(names[i], names[j])
                    name_similarities.append(sim)
            
            if name_similarities:
                entity.name_consistency_score = statistics.mean(name_similarities)
                confidence_factors.append(entity.name_consistency_score)
        else:
            entity.name_consistency_score = 1.0
            confidence_factors.append(1.0)
        
        # Document frequency (entities appearing in multiple documents are more reliable)
        doc_freq_score = min(entity.document_frequency / 3.0, 1.0)  # Normalize to max 3 documents
        confidence_factors.append(doc_freq_score)
        
        # Mention frequency (more mentions generally indicate higher confidence)
        mention_freq_score = min(entity.total_mentions / 5.0, 1.0)  # Normalize to max 5 mentions
        confidence_factors.append(mention_freq_score)
        
        # Context coherence (placeholder - could be improved with semantic analysis)
        if entity.contexts:
            # Simple coherence based on context length variation
            context_lengths = [len(ctx) for ctx in entity.contexts]
            if len(context_lengths) > 1:
                coherence = 1.0 - (statistics.stdev(context_lengths) / statistics.mean(context_lengths))
                entity.context_coherence_score = max(0.0, min(1.0, coherence))
            else:
                entity.context_coherence_score = 0.8  # Single context gets moderate score
        else:
            entity.context_coherence_score = 0.5  # No context gets neutral score
        
        confidence_factors.append(entity.context_coherence_score)
        
        # Return weighted average
        return statistics.mean(confidence_factors)
    
    def deduplicate_entities(self, entity_profiles: List[EntityProfile]) -> List[EntityProfile]:
        """Additional deduplication pass on entity profiles"""
        if len(entity_profiles) <= 1:
            return entity_profiles
        
        # Group by entity type
        by_type = defaultdict(list)
        for entity in entity_profiles:
            by_type[entity.entity_type].append(entity)
        
        deduplicated_entities = []
        
        for entity_type, entities in by_type.items():
            if len(entities) <= 1:
                deduplicated_entities.extend(entities)
                continue
            
            # Find duplicates within same type
            duplicate_groups = self._find_duplicate_entities(entities)
            
            # Merge duplicates
            merged_entities = self._merge_duplicate_groups(duplicate_groups)
            deduplicated_entities.extend(merged_entities)
        
        return deduplicated_entities
    
    def _find_duplicate_entities(self, entities: List[EntityProfile]) -> List[List[EntityProfile]]:
        """Find groups of duplicate entities"""
        n = len(entities)
        similarity_matrix = np.zeros((n, n)) if SIMILARITY_AVAILABLE else [[0.0] * n for _ in range(n)]
        
        # Calculate similarity between entity canonical names
        for i in range(n):
            for j in range(i, n):
                if i == j:
                    sim = 1.0
                else:
                    sim = self.string_calculator.calculate_similarity(
                        entities[i].canonical_name,
                        entities[j].canonical_name
                    )
                
                if SIMILARITY_AVAILABLE:
                    similarity_matrix[i][j] = sim
                    similarity_matrix[j][i] = sim
                else:
                    similarity_matrix[i][j] = sim
                    similarity_matrix[j][i] = sim
        
        # Group highly similar entities
        groups = []
        assigned = [False] * n
        
        for i in range(n):
            if assigned[i]:
                continue
            
            group = [entities[i]]
            assigned[i] = True
            
            for j in range(i + 1, n):
                if assigned[j]:
                    continue
                
                if SIMILARITY_AVAILABLE:
                    sim = similarity_matrix[i][j]
                else:
                    sim = similarity_matrix[i][j]
                
                if sim >= 0.9:  # High threshold for entity-level deduplication
                    group.append(entities[j])
                    assigned[j] = True
            
            groups.append(group)
        
        return groups
    
    def _merge_duplicate_groups(self, duplicate_groups: List[List[EntityProfile]]) -> List[EntityProfile]:
        """Merge duplicate entity groups"""
        merged_entities = []
        
        for group in duplicate_groups:
            if len(group) == 1:
                merged_entities.append(group[0])
            else:
                # Merge all entities in group into the one with most mentions
                target_entity = max(group, key=lambda e: e.total_mentions)
                
                for entity in group:
                    if entity.entity_id != target_entity.entity_id:
                        # Merge mentions
                        target_entity.mentions.extend(entity.mentions)
                        target_entity.alternative_names.update(entity.alternative_names)
                        target_entity.documents.update(entity.documents)
                        target_entity.contexts.extend(entity.contexts)
                        
                        # Update aggregated metrics
                        target_entity.total_mentions = len(target_entity.mentions)
                        target_entity.document_frequency = len(target_entity.documents)
                        
                        # Merge attributes
                        for key, value in entity.attributes.items():
                            if key not in target_entity.attributes:
                                target_entity.attributes[key] = value
                
                merged_entities.append(target_entity)
        
        return merged_entities
    
    def get_linking_statistics(self) -> Dict[str, Any]:
        """Get entity linking statistics"""
        stats = dict(self.linking_stats)
        
        # Add component information
        stats['components'] = {
            'string_calculator': self.string_calculator.get_calculator_info(),
            'semantic_calculator': (
                self.semantic_calculator.get_calculator_info() 
                if self.semantic_calculator else None
            )
        }
        
        # Add current state
        stats['current_entities'] = len(self.entity_profiles)
        stats['current_mentions'] = sum(len(e.mentions) for e in self.entity_profiles.values())
        
        return stats
    
    def export_entity_profiles(self, export_path: str, 
                             include_mentions: bool = True,
                             include_contexts: bool = False) -> bool:
        """Export entity profiles to JSON file"""
        try:
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "total_entities": len(self.entity_profiles),
                "linking_statistics": self.get_linking_statistics(),
                "entities": []
            }
            
            for entity in self.entity_profiles.values():
                entity_data = {
                    "entity_id": entity.entity_id,
                    "canonical_name": entity.canonical_name,
                    "entity_type": entity.entity_type.value,
                    "alternative_names": list(entity.alternative_names),
                    "total_mentions": entity.total_mentions,
                    "document_frequency": entity.document_frequency,
                    "documents": list(entity.documents),
                    "name_consistency_score": entity.name_consistency_score,
                    "context_coherence_score": entity.context_coherence_score,
                    "overall_confidence": entity.overall_confidence,
                    "attributes": entity.attributes,
                    "created_at": entity.created_at.isoformat(),
                    "updated_at": entity.updated_at.isoformat()
                }
                
                if include_mentions:
                    entity_data["mentions"] = [
                        {
                            "mention_id": m.mention_id,
                            "text": m.text,
                            "normalized_text": m.normalized_text,
                            "document_id": m.document_id,
                            "start_position": m.start_position,
                            "end_position": m.end_position,
                            "confidence": m.confidence,
                            "context": m.context if include_contexts else "",
                            "metadata": m.metadata
                        }
                        for m in entity.mentions
                    ]
                
                if include_contexts:
                    entity_data["primary_context"] = entity.get_primary_context()
                
                export_data["entities"].append(entity_data)
            
            # Write to file
            export_path = Path(export_path)
            export_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, default=str, ensure_ascii=False)
            
            logger.info(f"Exported {len(self.entity_profiles)} entity profiles to {export_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export entity profiles: {e}")
            return False


# Factory functions for common use cases
def create_entity_linker(similarity_threshold: float = 0.8,
                        use_semantic: bool = True) -> EntityLinker:
    """Create entity linker with optimal settings"""
    return EntityLinker(
        string_similarity_threshold=similarity_threshold,
        semantic_similarity_threshold=0.7,
        use_semantic_similarity=use_semantic
    )


# Example usage and testing
if __name__ == "__main__":
    def test_entity_linking():
        # Create entity linker
        linker = create_entity_linker()
        
        print("Entity Linking and Deduplication Test")
        print("=" * 50)
        
        # Create test mentions
        test_mentions = [
            # Person entities with variations
            EntityMention(
                mention_id="", text="Barack Obama", normalized_text="Barack Obama",
                document_id="doc1", start_position=10, end_position=22,
                entity_type=EntityType.PERSON, confidence=0.95,
                context="Former president Barack Obama spoke at the event"
            ),
            EntityMention(
                mention_id="", text="Obama", normalized_text="Obama", 
                document_id="doc2", start_position=5, end_position=10,
                entity_type=EntityType.PERSON, confidence=0.8,
                context="Obama's policies were discussed"
            ),
            EntityMention(
                mention_id="", text="President Obama", normalized_text="President Obama",
                document_id="doc3", start_position=15, end_position=30,
                entity_type=EntityType.PERSON, confidence=0.9,
                context="President Obama announced new initiatives"
            ),
            
            # Organization entities
            EntityMention(
                mention_id="", text="Apple Inc.", normalized_text="Apple Inc.",
                document_id="doc1", start_position=50, end_position=60,
                entity_type=EntityType.ORGANIZATION, confidence=0.95,
                context="Apple Inc. released new products"
            ),
            EntityMention(
                mention_id="", text="Apple", normalized_text="Apple",
                document_id="doc2", start_position=20, end_position=25,
                entity_type=EntityType.ORGANIZATION, confidence=0.85,
                context="Apple stock prices rose"
            ),
            
            # Location entities
            EntityMention(
                mention_id="", text="New York City", normalized_text="New York City",
                document_id="doc1", start_position=100, end_position=113,
                entity_type=EntityType.LOCATION, confidence=0.9,
                context="Located in New York City"
            ),
            EntityMention(
                mention_id="", text="NYC", normalized_text="NYC",
                document_id="doc3", start_position=40, end_position=43,
                entity_type=EntityType.LOCATION, confidence=0.8,
                context="NYC weather forecast"
            ),
        ]
        
        print(f"Test data: {len(test_mentions)} mentions")
        for mention in test_mentions:
            print(f"  - {mention.text} ({mention.entity_type.value}) in {mention.document_id}")
        
        # Perform entity linking
        print("\nPerforming entity linking...")
        result = linker.link_mentions(test_mentions)
        
        print(f"\nLinking Results:")
        print(f"  Total mentions: {result.total_mentions}")
        print(f"  Total entities: {result.total_entities}")
        print(f"  Processing time: {result.processing_time:.3f}s")
        print(f"  Average confidence: {result.average_confidence:.3f}")
        print(f"  Method used: {result.method_used}")
        
        # Show entity profiles
        print(f"\nEntity Profiles:")
        for i, entity in enumerate(result.entity_profiles):
            print(f"\n{i+1}. {entity.canonical_name} ({entity.entity_type.value})")
            print(f"   Entity ID: {entity.entity_id}")
            print(f"   Total mentions: {entity.total_mentions}")
            print(f"   Documents: {len(entity.documents)}")
            print(f"   Alternative names: {list(entity.alternative_names)}")
            print(f"   Confidence: {entity.overall_confidence:.3f}")
            print(f"   Name consistency: {entity.name_consistency_score:.3f}")
            
            print(f"   Mentions:")
            for mention in entity.mentions:
                print(f"     - '{mention.text}' in {mention.document_id} (conf: {mention.confidence:.2f})")
            
            if entity.contexts:
                primary_context = entity.get_primary_context(100)
                print(f"   Primary context: {primary_context}")
        
        # Test deduplication
        print(f"\nTesting deduplication...")
        deduplicated = linker.deduplicate_entities(result.entity_profiles)
        print(f"After deduplication: {len(deduplicated)} entities (was {len(result.entity_profiles)})")
        
        # Show statistics
        print(f"\nLinking Statistics:")
        stats = linker.get_linking_statistics()
        for key, value in stats.items():
            if key != 'components':
                print(f"  {key}: {value}")
        
        # Export results
        if linker.export_entity_profiles("test_entity_profiles.json", include_contexts=True):
            print("\nEntity profiles exported to test_entity_profiles.json")
    
    test_entity_linking()