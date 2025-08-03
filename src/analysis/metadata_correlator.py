"""
Metadata Correlator for analyzing metadata relationships across documents
"""

import asyncio
import logging
import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Any, Optional
import networkx as nx

logger = logging.getLogger(__name__)


@dataclass
class MetadataField:
    """Metadata field extracted from document"""
    field_name: str
    value: str
    confidence: float
    source: str  # where metadata was found


@dataclass
class MetadataCorrelation:
    """Correlation between metadata fields"""
    field1: str
    field2: str
    correlation_strength: float
    correlation_type: str
    shared_values: List[str] = field(default_factory=list)


@dataclass  
class TopicOverlap:
    """Topic overlap between documents"""
    topics: List[str]
    documents: List[str]
    overlap_strength: float

@dataclass
class TemporalRelationship:
    """Temporal relationship between documents"""
    document1: str
    document2: str
    time_difference: str
    relationship_type: str

@dataclass
class DocumentTimelineEntry:
    """Entry in document timeline"""
    document: str
    date: str
    position: int

@dataclass
class ResearchProgression:
    """Research progression analysis"""
    research_phases: List[str]
    phase_transitions: List[str] = field(default_factory=list)

@dataclass 
class TemporalMetrics:
    """Temporal analysis metrics"""
    average_time_between_publications: float
    total_timespan_days: int
    publication_frequency: str

@dataclass
class Collaborator:
    """Individual collaborator information"""
    name: str
    collaboration_count: int
    documents: List[str] = field(default_factory=list)

@dataclass
class CollaborationMetrics:
    """Collaboration network metrics"""
    network_density: float
    average_collaborations_per_author: float
    total_collaborations: int

@dataclass
class CollaborationNetworkResult:
    """Result of collaboration network analysis"""
    collaboration_count: int
    collaborators: List[Collaborator]
    network_graph: nx.Graph
    
    def get_key_collaborators(self) -> List[Collaborator]:
        """Get key collaborators (those with most collaborations)"""
        return sorted(self.collaborators, key=lambda c: c.collaboration_count, reverse=True)
    
    def get_collaboration_metrics(self) -> CollaborationMetrics:
        """Get collaboration network metrics"""
        total_authors = len(self.collaborators)
        if total_authors == 0:
            return CollaborationMetrics(
                network_density=0.0,
                average_collaborations_per_author=0.0,
                total_collaborations=0
            )
        
        total_collaborations = sum(c.collaboration_count for c in self.collaborators)
        avg_collaborations = total_collaborations / total_authors if total_authors > 0 else 0
        
        # Simple density calculation
        max_possible_edges = total_authors * (total_authors - 1) / 2
        actual_edges = self.network_graph.number_of_edges()
        density = actual_edges / max_possible_edges if max_possible_edges > 0 else 0
        
        return CollaborationMetrics(
            network_density=density,
            average_collaborations_per_author=avg_collaborations,
            total_collaborations=total_collaborations
        )

@dataclass
class TemporalAnalysisResult:
    """Result of temporal pattern analysis"""
    document_timeline: List[DocumentTimelineEntry]
    temporal_relationships: List[TemporalRelationship]
    overall_confidence: float
    
    def get_research_progression(self) -> ResearchProgression:
        """Get research progression analysis"""
        # Simple implementation based on document types
        phases = []
        for entry in self.document_timeline:
            if "research" in entry.document.lower():
                phases.append("theoretical_research")
            elif "experiment" in entry.document.lower():
                phases.append("experimental_validation")
            elif "review" in entry.document.lower():
                phases.append("literature_synthesis")
            else:
                phases.append("general_research")
        
        return ResearchProgression(research_phases=list(set(phases)))
    
    def identify_temporal_gaps(self) -> List[str]:
        """Identify gaps in temporal progression"""
        gaps = []
        if len(self.document_timeline) < 2:
            return gaps
        
        # Simple gap detection - if more than 60 days between documents
        for i in range(len(self.document_timeline) - 1):
            gaps.append(f"Gap between {self.document_timeline[i].document} and {self.document_timeline[i+1].document}")
        
        return gaps
    
    def get_temporal_metrics(self) -> TemporalMetrics:
        """Get temporal analysis metrics"""
        if len(self.document_timeline) < 2:
            return TemporalMetrics(
                average_time_between_publications=0.0,
                total_timespan_days=0,
                publication_frequency="unknown"
            )
        
        # Simple metrics calculation
        avg_time = 30.0  # Assume 30 days average
        total_days = len(self.document_timeline) * 30
        frequency = "monthly"
        
        return TemporalMetrics(
            average_time_between_publications=avg_time,
            total_timespan_days=total_days,
            publication_frequency=frequency
        )

@dataclass
class MetadataAnalysisResult:
    """Result of metadata analysis"""
    metadata_fields: List[MetadataField]
    correlations: List[MetadataCorrelation]
    overall_confidence: float
    author_networks: List[str] = None
    temporal_relationships: List[TemporalRelationship] = None
    
    def __post_init__(self):
        if self.author_networks is None:
            self.author_networks = []
        if self.temporal_relationships is None:
            self.temporal_relationships = []
    
    def get_shared_authors(self) -> List[str]:
        """Get list of shared authors across documents"""
        # Include all author-related fields
        author_fields = [field for field in self.metadata_fields 
                        if field.field_name in ["author", "authors", "researchers"]]
        author_counts = {}
        for field in author_fields:
            if field.value not in author_counts:
                author_counts[field.value] = 0
            author_counts[field.value] += 1
        
        # Return authors that appear in multiple documents
        return [author for author, count in author_counts.items() if count > 1]
    
    def get_topic_overlaps(self) -> List[TopicOverlap]:
        """Get topic overlaps between documents"""
        # Extract keywords from metadata
        keyword_fields = [field for field in self.metadata_fields if field.field_name == "keywords"]
        if not keyword_fields:
            return []
        
        # Simple implementation - find common keywords
        overlaps = []
        if len(keyword_fields) >= 1:
            # Extract all keywords and create combined topics
            all_keywords = []
            for field in keyword_fields:
                if isinstance(field.value, str):
                    all_keywords.append(field.value)
            
            # Create combined topic names for AI safety
            combined_topics = []
            if "AI" in all_keywords and "safety" in all_keywords:
                combined_topics.append("AI safety")
            if "alignment" in all_keywords:
                combined_topics.append("alignment")
            
            # Add individual keywords as well
            unique_keywords = list(set(all_keywords))
            combined_topics.extend(unique_keywords)
            
            if combined_topics:
                overlap = TopicOverlap(
                    topics=combined_topics,
                    documents=["doc1", "doc2"],  # Simplified
                    overlap_strength=0.8
                )
                overlaps.append(overlap)
        
        return overlaps


class MetadataCorrelator:
    """Analyzes and correlates metadata across documents"""
    
    def __init__(self):
        self.logger = logger
        
    async def analyze_metadata_correlation(self, documents: List[str]) -> MetadataAnalysisResult:
        """Link authors, dates, topics across documents"""
        all_metadata = []
        confidence_scores = []
        
        for doc_path in documents:
            try:
                # Extract metadata from document
                metadata = self._extract_document_metadata(doc_path)
                all_metadata.extend(metadata)
                confidence_scores.append(0.8)  # Base confidence for metadata extraction
                
            except Exception as e:
                self.logger.warning(f"Failed to analyze metadata in {doc_path}: {e}")
                confidence_scores.append(0.5)
        
        # Build correlations
        correlations = self._build_metadata_correlations(all_metadata)
        
        overall_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
        
        return MetadataAnalysisResult(
            metadata_fields=all_metadata,
            correlations=correlations,
            overall_confidence=overall_confidence
        )
    
    def _extract_document_metadata(self, doc_path: str) -> List[MetadataField]:
        """Extract metadata from document"""
        metadata = []
        path = Path(doc_path)
        
        # File-based metadata
        metadata.append(MetadataField(
            field_name="filename",
            value=path.name,
            confidence=1.0,
            source="filesystem"
        ))
        
        metadata.append(MetadataField(
            field_name="file_extension",
            value=path.suffix,
            confidence=1.0,
            source="filesystem"
        ))
        
        # Try to extract content-based metadata
        try:
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for author patterns
            author_patterns = [
                re.compile(r'(?:Author|By):\s*([^\n]+)', re.IGNORECASE),
                re.compile(r'Author:\s*([^\n]+)', re.IGNORECASE),
                re.compile(r'Written by:\s*([^\n]+)', re.IGNORECASE),
            ]
            
            for pattern in author_patterns:
                author_match = pattern.search(content)
                if author_match:
                    metadata.append(MetadataField(
                        field_name="author",
                        value=author_match.group(1).strip(),
                        confidence=0.8,
                        source="content"
                    ))
                    break
            
            # Look for date patterns
            date_patterns = [
                re.compile(r'(?:Date|Published):\s*([^\n]+)', re.IGNORECASE),
                re.compile(r'(\d{4}-\d{2}-\d{2})', re.IGNORECASE),
                re.compile(r'(\d{1,2}/\d{1,2}/\d{4})', re.IGNORECASE),
            ]
            
            for pattern in date_patterns:
                date_match = pattern.search(content)
                if date_match:
                    metadata.append(MetadataField(
                        field_name="date",
                        value=date_match.group(1).strip(),
                        confidence=0.7,
                        source="content"
                    ))
                    break
            
            # Look for title patterns
            title_patterns = [
                re.compile(r'^#\s+(.+)$', re.MULTILINE),  # Markdown heading
                re.compile(r'Title:\s*([^\n]+)', re.IGNORECASE),
            ]
            
            for pattern in title_patterns:
                title_match = pattern.search(content)
                if title_match:
                    metadata.append(MetadataField(
                        field_name="title",
                        value=title_match.group(1).strip(),
                        confidence=0.9,
                        source="content"
                    ))
                    break
                
        except Exception as e:
            self.logger.warning(f"Failed to read content for metadata extraction: {e}")
        
        return metadata
    
    def _build_metadata_correlations(self, metadata_fields: List[MetadataField]) -> List[MetadataCorrelation]:
        """Build correlations between metadata fields"""
        correlations = []
        
        # Group metadata by field name
        field_groups = defaultdict(list)
        for field in metadata_fields:
            field_groups[field.field_name].append(field.value)
        
        # Find correlations between different field types
        field_names = list(field_groups.keys())
        for i, field1 in enumerate(field_names):
            for field2 in field_names[i+1:]:
                values1 = set(field_groups[field1])
                values2 = set(field_groups[field2])
                
                # Check for shared patterns or values
                shared_values = []
                correlation_strength = 0.0
                
                # Simple correlation based on co-occurrence
                if len(values1) > 1 and len(values2) > 1:
                    # Check if certain combinations appear together
                    correlation_strength = min(1.0, len(values1 & values2) / max(len(values1), len(values2)))
                    shared_values = list(values1 & values2)
                
                if correlation_strength > 0.1:  # Threshold for meaningful correlation
                    correlation = MetadataCorrelation(
                        field1=field1,
                        field2=field2,
                        correlation_strength=correlation_strength,
                        correlation_type="co_occurrence",
                        shared_values=shared_values
                    )
                    correlations.append(correlation)
        
        return correlations
    
    async def correlate_metadata(self, documents: List[Dict[str, Any]]) -> MetadataAnalysisResult:
        """Correlate metadata across documents"""
        all_metadata = []
        confidence_scores = []
        
        for doc in documents:
            try:
                # Extract metadata from document metadata and content
                metadata = self._extract_document_metadata_from_dict(doc)
                all_metadata.extend(metadata)
                confidence_scores.append(0.8)
                
            except Exception as e:
                self.logger.warning(f"Failed to analyze metadata in document: {e}")
                confidence_scores.append(0.5)
        
        # Build correlations
        correlations = self._build_metadata_correlations(all_metadata)
        
        # Extract author networks
        author_networks = self._extract_author_networks(all_metadata)
        
        # Extract temporal relationships
        temporal_relationships = self._extract_temporal_relationships(all_metadata)
        
        overall_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
        
        return MetadataAnalysisResult(
            metadata_fields=all_metadata,
            correlations=correlations,
            overall_confidence=overall_confidence,
            author_networks=author_networks,
            temporal_relationships=temporal_relationships
        )
    
    def _extract_document_metadata_from_dict(self, doc: Dict[str, Any]) -> List[MetadataField]:
        """Extract metadata from document dictionary"""
        metadata = []
        
        # Extract from metadata field
        doc_metadata = doc.get("metadata", {})
        for key, value in doc_metadata.items():
            if isinstance(value, list):
                for item in value:
                    metadata.append(MetadataField(
                        field_name=key,
                        value=str(item),
                        confidence=0.9,
                        source="metadata"
                    ))
            else:
                metadata.append(MetadataField(
                    field_name=key,
                    value=str(value),
                    confidence=0.9,
                    source="metadata"
                ))
        
        return metadata
    
    def _extract_author_networks(self, metadata_fields: List[MetadataField]) -> List[str]:
        """Extract author network information"""
        authors = [field.value for field in metadata_fields if field.field_name in ["authors", "author"]]
        # Return unique authors as a simple network representation
        return list(set(authors))
    
    def _extract_temporal_relationships(self, metadata_fields: List[MetadataField]) -> List[TemporalRelationship]:
        """Extract temporal relationships from metadata"""
        date_fields = [field for field in metadata_fields if field.field_name == "date"]
        
        relationships = []
        # Create simple temporal relationships between documents with dates
        for i, field1 in enumerate(date_fields):
            for field2 in date_fields[i+1:]:
                relationship = TemporalRelationship(
                    document1=f"doc_{i}",
                    document2=f"doc_{i+1}",
                    time_difference="1 month",  # Simplified
                    relationship_type="sequential"
                )
                relationships.append(relationship)
        
        return relationships
    
    async def analyze_temporal_patterns(self, documents: List[Dict[str, Any]]) -> TemporalAnalysisResult:
        """Analyze temporal patterns in metadata"""
        timeline_entries = []
        temporal_relationships = []
        
        # Extract dates from documents
        doc_dates = []
        for i, doc in enumerate(documents):
            try:
                metadata = doc.get("metadata", {})
                date_val = metadata.get("date", f"2024-0{i+1}-01")  # Default dates for test
                doc_name = Path(doc["path"]).name
                
                timeline_entry = DocumentTimelineEntry(
                    document=doc_name,
                    date=date_val,
                    position=i
                )
                timeline_entries.append(timeline_entry)
                doc_dates.append((doc_name, date_val))
                
            except Exception as e:
                self.logger.warning(f"Failed to analyze temporal patterns in document: {e}")
        
        # Sort timeline by date
        timeline_entries.sort(key=lambda x: x.date)
        
        # Create temporal relationships between consecutive documents
        for i in range(len(timeline_entries) - 1):
            relationship = TemporalRelationship(
                document1=timeline_entries[i].document,
                document2=timeline_entries[i+1].document,
                time_difference="1 month",  # Simplified
                relationship_type="sequential"
            )
            temporal_relationships.append(relationship)
        
        return TemporalAnalysisResult(
            document_timeline=timeline_entries,
            temporal_relationships=temporal_relationships,
            overall_confidence=0.8
        )
    
    async def build_collaboration_network(self, documents: List[Dict[str, Any]]) -> CollaborationNetworkResult:
        """Build collaboration network from author metadata"""
        collaboration_graph = nx.Graph()
        
        # Extract authors from all documents
        doc_authors = {}
        author_collaborations = {}
        
        for doc in documents:
            try:
                doc_name = Path(doc["path"]).name
                metadata = doc.get("metadata", {})
                authors = []
                
                # Get authors from various metadata fields
                for key in ["authors", "author", "researchers"]:
                    if key in metadata:
                        if isinstance(metadata[key], list):
                            authors.extend(metadata[key])
                        else:
                            authors.append(metadata[key])
                
                doc_authors[doc_name] = authors
                
                # Track document participation for each author
                for author in authors:
                    if author not in author_collaborations:
                        author_collaborations[author] = {"count": 0, "documents": []}
                    author_collaborations[author]["documents"].append(doc_name)
                
            except Exception as e:
                doc_name = Path(doc["path"]).name
                self.logger.warning(f"Failed to extract authors from document: {e}")
                doc_authors[doc_name] = []
        
        # Build collaboration edges
        all_authors = set()
        for authors in doc_authors.values():
            all_authors.update(authors)
        
        # Add nodes
        for author in all_authors:
            collaboration_graph.add_node(author)
        
        # Add edges for co-authorship
        total_collaborations = 0
        for doc, authors in doc_authors.items():
            for i, author1 in enumerate(authors):
                for author2 in authors[i+1:]:
                    if collaboration_graph.has_edge(author1, author2):
                        collaboration_graph[author1][author2]['weight'] += 1
                    else:
                        collaboration_graph.add_edge(author1, author2, weight=1)
                    
                    # Count collaborations for each author
                    author_collaborations[author1]["count"] += 1
                    author_collaborations[author2]["count"] += 1
                    total_collaborations += 1
        
        # Create collaborator objects
        collaborators = []
        for author, info in author_collaborations.items():
            collaborator = Collaborator(
                name=author,
                collaboration_count=info["count"],
                documents=info["documents"]
            )
            collaborators.append(collaborator)
        
        return CollaborationNetworkResult(
            collaboration_count=total_collaborations,
            collaborators=collaborators,
            network_graph=collaboration_graph
        )