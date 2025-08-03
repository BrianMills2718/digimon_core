"""
Concept Tracker for tracking how concepts evolve across documents.

This module analyzes how concepts, ideas, and technologies develop and change
over time across multiple documents.
"""

import asyncio
import logging
import re
import numpy as np
from typing import List, Dict, Any, Set, Tuple, Optional
from dataclasses import dataclass, field
from collections import defaultdict, Counter
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class ConceptMention:
    """A mention of a concept in a document"""
    concept_name: str
    document_path: str
    mention_context: str
    timestamp: str
    sentiment: str  # positive, negative, neutral
    confidence_score: float
    position_in_doc: int
    related_entities: List[str] = field(default_factory=list)


@dataclass
class ConceptEvolution:
    """Tracks how a concept evolves across documents"""
    concept_id: str
    concept_name: str
    timeline: List[Dict[str, Any]]
    evolution_type: str  # emerging, evolving, declining, stable
    confidence_score: float
    key_milestones: List[Dict[str, Any]] = field(default_factory=list)
    evolution_metrics: Dict[str, float] = field(default_factory=dict)


@dataclass
class ConceptEvolutionResult:
    """Result of concept evolution tracking"""
    concept_evolutions: List[ConceptEvolution]
    evolution_statistics: Dict[str, Any]
    temporal_patterns: Dict[str, Any]


class ConceptTracker:
    """
    Tracks concept evolution across documents and time.
    """
    
    def __init__(self):
        self.logger = logger
        self.concept_cache = {}
        self.evolution_patterns = {}
        
    async def track_concept_evolution(self, documents: List[Dict[str, Any]]) -> ConceptEvolutionResult:
        """Track how concepts evolve across documents"""
        self.logger.info(f"Tracking concept evolution in {len(documents)} documents")
        
        # Extract concept mentions from all documents
        all_concept_mentions = []
        for doc in documents:
            mentions = self._extract_concept_mentions(doc)
            all_concept_mentions.extend(mentions)
        
        # Group mentions by concept
        concepts_by_name = defaultdict(list)
        for mention in all_concept_mentions:
            normalized_name = self._normalize_concept_name(mention.concept_name)
            concepts_by_name[normalized_name].append(mention)
        
        # Track evolution for each concept
        concept_evolutions = []
        for concept_name, mentions in concepts_by_name.items():
            if len(mentions) >= 2:  # Need multiple mentions to track evolution
                evolution = self._analyze_concept_evolution(concept_name, mentions)
                if evolution:
                    concept_evolutions.append(evolution)
        
        # Calculate evolution statistics
        evolution_stats = self._calculate_evolution_statistics(concept_evolutions)
        
        # Identify temporal patterns
        temporal_patterns = self._identify_temporal_patterns(concept_evolutions)
        
        return ConceptEvolutionResult(
            concept_evolutions=concept_evolutions,
            evolution_statistics=evolution_stats,
            temporal_patterns=temporal_patterns
        )
    
    def _extract_concept_mentions(self, document: Dict[str, Any]) -> List[ConceptMention]:
        """Extract concept mentions from a document"""
        content = document.get("content", "")
        doc_path = document.get("path", "")
        metadata = document.get("metadata", {})
        doc_date = metadata.get("date", "")
        
        concept_mentions = []
        
        # Define concept patterns for different domains
        concept_patterns = {
            "technology": [
                r'\b(CRISPR(?:-[A-Za-z0-9]+)*)\b',
                r'\b(gene\s+editing|genetic\s+modification|gene\s+therapy)\b',
                r'\b(artificial\s+intelligence|machine\s+learning|neural\s+networks)\b',
                r'\b(blockchain|cryptocurrency|smart\s+contracts)\b',
                r'\b(renewable\s+energy|solar\s+power|wind\s+power)\b'
            ],
            "methodology": [
                r'\b(precision\s+medicine|personalized\s+medicine)\b',
                r'\b(clinical\s+trials|randomized\s+trials)\b',
                r'\b(peer\s+review|scientific\s+method)\b',
                r'\b(data\s+analysis|statistical\s+analysis)\b'
            ],
            "domain": [
                r'\b(biotechnology|bioengineering)\b',
                r'\b(bioethics|medical\s+ethics)\b',
                r'\b(climate\s+change|global\s+warming)\b',
                r'\b(sustainability|environmental\s+protection)\b'
            ],
            "outcome": [
                r'\b(breakthrough|innovation|discovery)\b',
                r'\b(treatment|therapy|cure)\b',
                r'\b(efficiency|effectiveness|improvement)\b',
                r'\b(risk|concern|challenge)\b'
            ]
        }
        
        # Extract concepts using patterns
        for category, patterns in concept_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    concept_name = match.group(1).strip()
                    
                    # Get context around mention
                    start_pos = max(0, match.start() - 75)
                    end_pos = min(len(content), match.end() + 75)
                    context = content[start_pos:end_pos].strip()
                    
                    # Analyze sentiment of mention
                    sentiment = self._analyze_concept_sentiment(context)
                    
                    # Extract related entities in context
                    related_entities = self._extract_related_entities(context)
                    
                    # Calculate confidence
                    confidence = self._calculate_mention_confidence(concept_name, context, category)
                    
                    if confidence > 0.5:
                        mention = ConceptMention(
                            concept_name=concept_name,
                            document_path=doc_path,
                            mention_context=context,
                            timestamp=doc_date or "unknown",
                            sentiment=sentiment,
                            confidence_score=confidence,
                            position_in_doc=match.start(),
                            related_entities=related_entities
                        )
                        concept_mentions.append(mention)
        
        # Also extract concepts from keywords
        keywords = metadata.get("keywords", [])
        for keyword in keywords:
            # Check if keyword is already captured
            if not any(self._concept_names_similar(keyword, mention.concept_name) 
                      for mention in concept_mentions):
                mention = ConceptMention(
                    concept_name=keyword,
                    document_path=doc_path,
                    mention_context=f"Keyword in document metadata: {doc_path}",
                    timestamp=doc_date or "unknown",
                    sentiment="neutral",
                    confidence_score=0.8,
                    position_in_doc=0,
                    related_entities=[]
                )
                concept_mentions.append(mention)
        
        return concept_mentions
    
    def _analyze_concept_evolution(self, concept_name: str, mentions: List[ConceptMention]) -> Optional[ConceptEvolution]:
        """Analyze how a concept evolves based on its mentions"""
        if len(mentions) < 2:
            return None
        
        # Sort mentions chronologically
        dated_mentions = [m for m in mentions if m.timestamp and m.timestamp != "unknown"]
        if len(dated_mentions) < 2:
            # If no dates, use document order as proxy
            timeline_events = self._create_timeline_from_mentions(mentions)
        else:
            sorted_mentions = sorted(dated_mentions, key=lambda x: x.timestamp)
            timeline_events = self._create_timeline_from_sorted_mentions(sorted_mentions)
        
        # Analyze evolution type
        evolution_type = self._classify_evolution_type(mentions, timeline_events)
        
        # Identify key milestones
        milestones = self._identify_concept_milestones(mentions)
        
        # Calculate evolution metrics
        evolution_metrics = self._calculate_evolution_metrics(mentions, timeline_events)
        
        # Calculate overall confidence
        confidence = np.mean([mention.confidence_score for mention in mentions])
        
        concept_evolution = ConceptEvolution(
            concept_id=f"concept_{concept_name.replace(' ', '_').lower()}",
            concept_name=concept_name,
            timeline=timeline_events,
            evolution_type=evolution_type,
            confidence_score=confidence,
            key_milestones=milestones,
            evolution_metrics=evolution_metrics
        )
        
        return concept_evolution
    
    def _create_timeline_from_sorted_mentions(self, sorted_mentions: List[ConceptMention]) -> List[Dict[str, Any]]:
        """Create timeline events from chronologically sorted mentions"""
        timeline_events = []
        
        for i, mention in enumerate(sorted_mentions):
            event = {
                "date": mention.timestamp,
                "description": self._summarize_mention(mention),
                "sentiment": mention.sentiment,
                "document": mention.document_path,
                "context": mention.mention_context[:100] + "..." if len(mention.mention_context) > 100 else mention.mention_context,
                "related_entities": mention.related_entities,
                "evolution_stage": self._determine_evolution_stage(i, len(sorted_mentions))
            }
            timeline_events.append(event)
        
        return timeline_events
    
    def _create_timeline_from_mentions(self, mentions: List[ConceptMention]) -> List[Dict[str, Any]]:
        """Create timeline when dates are not available"""
        timeline_events = []
        
        # Group by document and use document order
        doc_mentions = defaultdict(list)
        for mention in mentions:
            doc_mentions[mention.document_path].append(mention)
        
        # Sort documents by path (proxy for order)
        sorted_docs = sorted(doc_mentions.keys())
        
        for doc_path in sorted_docs:
            doc_mentions_list = doc_mentions[doc_path]
            for mention in doc_mentions_list:
                event = {
                    "date": mention.timestamp,
                    "description": self._summarize_mention(mention),
                    "sentiment": mention.sentiment,
                    "document": mention.document_path,
                    "context": mention.mention_context[:100] + "...",
                    "related_entities": mention.related_entities,
                    "evolution_stage": "unknown"
                }
                timeline_events.append(event)
        
        return timeline_events
    
    def _classify_evolution_type(self, mentions: List[ConceptMention], timeline_events: List[Dict[str, Any]]) -> str:
        """Classify the type of concept evolution"""
        # Analyze sentiment trends
        sentiments = [mention.sentiment for mention in mentions]
        sentiment_counts = Counter(sentiments)
        
        # Analyze mention frequency over time
        dated_mentions = [m for m in mentions if m.timestamp and m.timestamp != "unknown"]
        
        if len(dated_mentions) >= 3:
            # Sort by date and analyze trends
            sorted_mentions = sorted(dated_mentions, key=lambda x: x.timestamp)
            
            # Split into early and late periods
            mid_point = len(sorted_mentions) // 2
            early_mentions = sorted_mentions[:mid_point]
            late_mentions = sorted_mentions[mid_point:]
            
            # Compare mention frequencies
            if len(late_mentions) > len(early_mentions) * 1.5:
                return "emerging"
            elif len(early_mentions) > len(late_mentions) * 1.5:
                return "declining"
            else:
                # Check sentiment evolution
                early_positive = sum(1 for m in early_mentions if m.sentiment == "positive")
                late_positive = sum(1 for m in late_mentions if m.sentiment == "positive")
                
                if late_positive > early_positive:
                    return "evolving"
                else:
                    return "stable"
        
        # Fallback classification based on overall patterns
        if sentiment_counts.get("positive", 0) > sentiment_counts.get("negative", 0) * 2:
            return "emerging"
        elif sentiment_counts.get("negative", 0) > sentiment_counts.get("positive", 0) * 2:
            return "declining"
        else:
            return "stable"
    
    def _identify_concept_milestones(self, mentions: List[ConceptMention]) -> List[Dict[str, Any]]:
        """Identify key milestones in concept evolution"""
        milestones = []
        
        # Look for milestone indicators in mentions
        milestone_keywords = [
            "breakthrough", "discovery", "first", "pioneered", "developed", "created",
            "nobel", "award", "published", "patent", "approved", "launched"
        ]
        
        for mention in mentions:
            context_lower = mention.mention_context.lower()
            
            for keyword in milestone_keywords:
                if keyword in context_lower:
                    milestone = {
                        "date": mention.timestamp,
                        "type": keyword,
                        "description": mention.mention_context[:150] + "...",
                        "document": mention.document_path,
                        "importance_score": self._calculate_milestone_importance(mention, keyword)
                    }
                    milestones.append(milestone)
                    break  # Only one milestone type per mention
        
        # Sort milestones by importance and date
        milestones.sort(key=lambda x: (x["importance_score"], x["date"]), reverse=True)
        
        # Return top milestones
        return milestones[:5]
    
    def _calculate_evolution_metrics(self, mentions: List[ConceptMention], timeline_events: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate metrics for concept evolution"""
        metrics = {}
        
        # Frequency metrics
        metrics["total_mentions"] = len(mentions)
        metrics["documents_mentioning"] = len(set(mention.document_path for mention in mentions))
        metrics["avg_mentions_per_doc"] = metrics["total_mentions"] / metrics["documents_mentioning"]
        
        # Sentiment metrics
        sentiment_counts = Counter(mention.sentiment for mention in mentions)
        total_mentions = len(mentions)
        metrics["positive_sentiment_ratio"] = sentiment_counts.get("positive", 0) / total_mentions
        metrics["negative_sentiment_ratio"] = sentiment_counts.get("negative", 0) / total_mentions
        metrics["neutral_sentiment_ratio"] = sentiment_counts.get("neutral", 0) / total_mentions
        
        # Confidence metrics
        confidences = [mention.confidence_score for mention in mentions]
        metrics["avg_confidence"] = np.mean(confidences)
        metrics["min_confidence"] = np.min(confidences)
        metrics["max_confidence"] = np.max(confidences)
        
        # Evolution stability
        if len(timeline_events) > 1:
            sentiment_changes = 0
            for i in range(1, len(timeline_events)):
                if timeline_events[i]["sentiment"] != timeline_events[i-1]["sentiment"]:
                    sentiment_changes += 1
            metrics["sentiment_stability"] = 1.0 - (sentiment_changes / (len(timeline_events) - 1))
        else:
            metrics["sentiment_stability"] = 1.0
        
        # Entity association metrics
        all_entities = []
        for mention in mentions:
            all_entities.extend(mention.related_entities)
        
        unique_entities = len(set(all_entities))
        metrics["entity_diversity"] = unique_entities / max(1, len(all_entities)) if all_entities else 0.0
        metrics["avg_entities_per_mention"] = len(all_entities) / len(mentions) if mentions else 0.0
        
        return metrics
    
    def _calculate_evolution_statistics(self, concept_evolutions: List[ConceptEvolution]) -> Dict[str, Any]:
        """Calculate overall statistics for concept evolution"""
        if not concept_evolutions:
            return {}
        
        stats = {}
        
        # Evolution type distribution
        evolution_types = [evo.evolution_type for evo in concept_evolutions]
        type_counts = Counter(evolution_types)
        stats["evolution_type_distribution"] = dict(type_counts)
        
        # Timeline statistics
        timeline_lengths = [len(evo.timeline) for evo in concept_evolutions]
        stats["avg_timeline_length"] = np.mean(timeline_lengths)
        stats["max_timeline_length"] = np.max(timeline_lengths)
        stats["min_timeline_length"] = np.min(timeline_lengths)
        
        # Confidence statistics
        confidences = [evo.confidence_score for evo in concept_evolutions]
        stats["avg_evolution_confidence"] = np.mean(confidences)
        stats["high_confidence_concepts"] = sum(1 for c in confidences if c > 0.8)
        
        # Milestone statistics
        total_milestones = sum(len(evo.key_milestones) for evo in concept_evolutions)
        stats["total_milestones"] = total_milestones
        stats["avg_milestones_per_concept"] = total_milestones / len(concept_evolutions)
        
        # Most evolved concepts
        evolution_scores = []
        for evo in concept_evolutions:
            # Calculate evolution score based on multiple factors
            score = (
                len(evo.timeline) * 0.3 +
                len(evo.key_milestones) * 0.4 +
                evo.confidence_score * 0.3
            )
            evolution_scores.append((evo.concept_name, score))
        
        evolution_scores.sort(key=lambda x: x[1], reverse=True)
        stats["most_evolved_concepts"] = evolution_scores[:5]
        
        return stats
    
    def _identify_temporal_patterns(self, concept_evolutions: List[ConceptEvolution]) -> Dict[str, Any]:
        """Identify temporal patterns in concept evolution"""
        patterns = {}
        
        # Collect all timeline events
        all_events = []
        for evolution in concept_evolutions:
            for event in evolution.timeline:
                event_copy = event.copy()
                event_copy["concept"] = evolution.concept_name
                all_events.append(event_copy)
        
        # Filter events with valid dates
        dated_events = [event for event in all_events if event["date"] and event["date"] != "unknown"]
        
        if dated_events:
            # Sort events chronologically
            try:
                sorted_events = sorted(dated_events, key=lambda x: x["date"])
                patterns["chronological_events"] = sorted_events
                
                # Identify time periods of high activity
                date_counts = Counter(event["date"][:4] for event in sorted_events if len(event["date"]) >= 4)  # Group by year
                patterns["activity_by_year"] = dict(date_counts)
                
                # Most active periods
                if date_counts:
                    most_active_year = date_counts.most_common(1)[0]
                    patterns["most_active_period"] = most_active_year
                
            except (ValueError, KeyError) as e:
                self.logger.warning(f"Error processing temporal patterns: {e}")
                patterns["chronological_events"] = []
        
        # Concept emergence patterns
        emerging_concepts = [evo.concept_name for evo in concept_evolutions if evo.evolution_type == "emerging"]
        declining_concepts = [evo.concept_name for evo in concept_evolutions if evo.evolution_type == "declining"]
        
        patterns["emerging_concepts"] = emerging_concepts
        patterns["declining_concepts"] = declining_concepts
        
        # Co-evolution patterns (concepts that evolve together)
        co_evolution_pairs = self._find_co_evolution_patterns(concept_evolutions)
        patterns["co_evolution_pairs"] = co_evolution_pairs
        
        return patterns
    
    def _find_co_evolution_patterns(self, concept_evolutions: List[ConceptEvolution]) -> List[Tuple[str, str, float]]:
        """Find concepts that evolve together"""
        co_evolution_pairs = []
        
        for i, evo1 in enumerate(concept_evolutions):
            for evo2 in concept_evolutions[i+1:]:
                # Calculate co-evolution score based on timeline overlap
                overlap_score = self._calculate_timeline_overlap(evo1.timeline, evo2.timeline)
                
                # Check for entity overlap
                entities1 = set()
                entities2 = set()
                
                for event in evo1.timeline:
                    entities1.update(event.get("related_entities", []))
                for event in evo2.timeline:
                    entities2.update(event.get("related_entities", []))
                
                entity_overlap = len(entities1.intersection(entities2)) / max(1, len(entities1.union(entities2)))
                
                # Combined co-evolution score
                co_evolution_score = (overlap_score * 0.6 + entity_overlap * 0.4)
                
                if co_evolution_score > 0.3:  # Threshold for significant co-evolution
                    co_evolution_pairs.append((evo1.concept_name, evo2.concept_name, co_evolution_score))
        
        # Sort by co-evolution score
        co_evolution_pairs.sort(key=lambda x: x[2], reverse=True)
        
        return co_evolution_pairs[:10]  # Return top 10 pairs
    
    def _calculate_timeline_overlap(self, timeline1: List[Dict[str, Any]], timeline2: List[Dict[str, Any]]) -> float:
        """Calculate temporal overlap between two concept timelines"""
        dates1 = [event["date"] for event in timeline1 if event["date"] != "unknown"]
        dates2 = [event["date"] for event in timeline2 if event["date"] != "unknown"]
        
        if not dates1 or not dates2:
            return 0.0
        
        # Simple overlap based on shared dates (could be improved)
        common_dates = set(dates1).intersection(set(dates2))
        total_dates = set(dates1).union(set(dates2))
        
        return len(common_dates) / len(total_dates) if total_dates else 0.0
    
    # Helper methods
    def _normalize_concept_name(self, name: str) -> str:
        """Normalize concept name for grouping"""
        normalized = name.lower().strip()
        normalized = re.sub(r'\s+', ' ', normalized)  # Normalize whitespace
        normalized = re.sub(r'[^\w\s]', '', normalized)  # Remove punctuation
        return normalized
    
    def _concept_names_similar(self, name1: str, name2: str) -> bool:
        """Check if two concept names are similar"""
        from difflib import SequenceMatcher
        similarity = SequenceMatcher(None, name1.lower(), name2.lower()).ratio()
        return similarity > 0.8
    
    def _analyze_concept_sentiment(self, context: str) -> str:
        """Analyze sentiment of concept mention in context"""
        context_lower = context.lower()
        
        positive_indicators = [
            "breakthrough", "successful", "effective", "promising", "beneficial", 
            "innovative", "advanced", "improved", "excellent", "outstanding",
            "revolutionary", "pioneering", "cutting-edge"
        ]
        
        negative_indicators = [
            "failed", "unsuccessful", "dangerous", "risky", "harmful", "concerning",
            "problematic", "controversial", "limited", "insufficient", "flawed",
            "criticized", "questionable"
        ]
        
        positive_count = sum(1 for indicator in positive_indicators if indicator in context_lower)
        negative_count = sum(1 for indicator in negative_indicators if indicator in context_lower)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    def _extract_related_entities(self, context: str) -> List[str]:
        """Extract related entities from concept mention context"""
        entities = []
        
        # Simple entity extraction patterns
        patterns = [
            r'\b(?:Dr\.|Prof\.)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:University|Institute|Lab)\b',
            r'\b([A-Z]{2,})\b'  # Acronyms
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, context)
            entities.extend(matches)
        
        # Filter and clean
        filtered_entities = []
        for entity in entities:
            entity = entity.strip()
            if len(entity) > 2 and entity not in ["The", "This", "That"]:
                filtered_entities.append(entity)
        
        return list(set(filtered_entities))  # Remove duplicates
    
    def _calculate_mention_confidence(self, concept_name: str, context: str, category: str) -> float:
        """Calculate confidence for concept mention"""
        confidence = 0.6  # Base confidence
        
        # Boost for clear concept indicators
        if category == "technology" and concept_name.isupper():
            confidence += 0.2  # Acronyms are often clear technology concepts
        
        # Boost for specific context indicators
        context_lower = context.lower()
        
        concept_indicators = [
            "technology", "technique", "method", "approach", "system",
            "development", "research", "study", "analysis"
        ]
        
        for indicator in concept_indicators:
            if indicator in context_lower:
                confidence += 0.1
                break
        
        # Reduce confidence for very common terms
        common_terms = ["research", "study", "work", "analysis", "system"]
        if concept_name.lower() in common_terms:
            confidence -= 0.2
        
        return max(0.0, min(1.0, confidence))
    
    def _summarize_mention(self, mention: ConceptMention) -> str:
        """Create a summary description for a concept mention"""
        # Extract key action or descriptor from context
        context = mention.mention_context
        
        # Look for action verbs near the concept
        action_patterns = [
            r'(\w+(?:ed|ing|es|s)?)\s+.*?' + re.escape(mention.concept_name),
            re.escape(mention.concept_name) + r'.*?(\w+(?:ed|ing|es|s)?)'
        ]
        
        for pattern in action_patterns:
            match = re.search(pattern, context, re.IGNORECASE)
            if match:
                action = match.group(1)
                if action.lower() not in ["the", "and", "or", "but", "in", "on", "at"]:
                    return f"{mention.concept_name} {action}"
        
        # Fallback to sentiment-based description
        sentiment_descriptions = {
            "positive": f"Positive development in {mention.concept_name}",
            "negative": f"Concerns about {mention.concept_name}",
            "neutral": f"Discussion of {mention.concept_name}"
        }
        
        return sentiment_descriptions.get(mention.sentiment, f"Mention of {mention.concept_name}")
    
    def _determine_evolution_stage(self, position: int, total: int) -> str:
        """Determine evolution stage based on position in timeline"""
        ratio = position / max(1, total - 1)
        
        if ratio < 0.3:
            return "early"
        elif ratio < 0.7:
            return "development"
        else:
            return "mature"
    
    def _calculate_milestone_importance(self, mention: ConceptMention, milestone_type: str) -> float:
        """Calculate importance score for a milestone"""
        importance = 0.5  # Base importance
        
        # Boost for certain milestone types
        high_importance_types = ["breakthrough", "discovery", "first", "nobel", "pioneered"]
        if milestone_type in high_importance_types:
            importance += 0.3
        
        # Boost for mentions with high confidence
        importance += mention.confidence_score * 0.2
        
        # Boost for positive sentiment
        if mention.sentiment == "positive":
            importance += 0.2
        
        return min(1.0, importance)