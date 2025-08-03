"""
Document Dependency Tracker

Tracks inter-document relationships including citations, references, and dependencies.
"""

import logging
import re
import asyncio
from typing import List, Dict, Set, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import networkx as nx

logger = logging.getLogger(__name__)


class DependencyType(Enum):
    """Types of document dependencies"""
    REFERENCE = "reference"
    CITATION = "citation" 
    INCLUSION = "inclusion"
    DEPENDENCY = "dependency"
    SIMILARITY = "similarity"


@dataclass
class DocumentDependency:
    """Represents a dependency between documents"""
    source_document: str
    target_document: str
    dependency_type: DependencyType
    confidence: float
    context: Optional[str] = None
    line_number: Optional[int] = None


@dataclass
class ReferenceGraph:
    """Graph of document references"""
    nodes: Set[str] = field(default_factory=set)
    edges: List[DocumentDependency] = field(default_factory=list)
    reference_chains: List[List[str]] = field(default_factory=list)
    
    @property
    def node_count(self) -> int:
        return len(self.nodes)
    
    @property 
    def edge_count(self) -> int:
        return len(self.edges)
    
    def get_references(self) -> List[DocumentDependency]:
        """Get all reference relationships"""
        return [edge for edge in self.edges if edge.dependency_type == DependencyType.REFERENCE]


class DocumentDependencyTracker:
    """Tracks dependencies between documents"""
    
    def __init__(self):
        """Initialize dependency tracker"""
        self.logger = logger
        self._reference_patterns = [
            # File references
            r'(?:see|refer to|check|view|open)\s+([a-zA-Z0-9_\-\.]+\.[a-zA-Z]{2,4})',
            # Document mentions
            r'document[_\s]+([a-zA-Z0-9_\-\.]+)',
            # Direct file names
            r'([a-zA-Z0-9_\-]+\.(?:pdf|txt|doc|docx|json|xml|md))',
            # Citation patterns
            r'(?:cited in|mentioned in|according to)\s+([a-zA-Z0-9_\-\.]+)',
        ]
        
        # Compile patterns for efficiency
        self._compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self._reference_patterns]
    
    async def detect_dependencies(self, document_paths: List[str]) -> List[DocumentDependency]:
        """Detect dependencies between documents"""
        self.logger.info(f"Detecting dependencies for {len(document_paths)} documents")
        
        dependencies = []
        
        # Create mapping of filenames to full paths
        filename_map = {}
        for doc_path in document_paths:
            filename = Path(doc_path).name
            filename_map[filename] = doc_path
        
        # Analyze each document for references
        for source_doc in document_paths:
            doc_dependencies = await self._analyze_document_references(
                source_doc, filename_map
            )
            dependencies.extend(doc_dependencies)
        
        self.logger.info(f"Found {len(dependencies)} dependencies")
        return dependencies
    
    async def _analyze_document_references(self, document_path: str, 
                                         filename_map: Dict[str, str]) -> List[DocumentDependency]:
        """Analyze a single document for references"""
        dependencies = []
        
        try:
            # Read document content
            with open(document_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            lines = content.splitlines()
            
            # Search for references in each line
            for line_num, line in enumerate(lines, 1):
                line_dependencies = self._extract_references_from_line(
                    line, document_path, filename_map, line_num
                )
                dependencies.extend(line_dependencies)
                
        except Exception as e:
            self.logger.warning(f"Failed to analyze references in {document_path}: {e}")
        
        return dependencies
    
    def _extract_references_from_line(self, line: str, source_doc: str, 
                                    filename_map: Dict[str, str], 
                                    line_num: int) -> List[DocumentDependency]:
        """Extract references from a single line"""
        dependencies = []
        
        for pattern in self._compiled_patterns:
            matches = pattern.findall(line)
            
            for match in matches:
                # Clean up the match
                referenced_file = match.strip()
                
                # Check if this file exists in our document set
                if referenced_file in filename_map:
                    target_doc = filename_map[referenced_file]
                    
                    # Don't create self-references
                    if target_doc != source_doc:
                        # Determine dependency type based on context
                        dep_type = self._classify_dependency_type(line, referenced_file)
                        confidence = self._calculate_confidence(line, referenced_file)
                        
                        dependency = DocumentDependency(
                            source_document=source_doc,
                            target_document=target_doc,
                            dependency_type=dep_type,
                            confidence=confidence,
                            context=line.strip(),
                            line_number=line_num
                        )
                        
                        dependencies.append(dependency)
        
        return dependencies
    
    def _classify_dependency_type(self, line: str, referenced_file: str) -> DependencyType:
        """Classify the type of dependency based on context"""
        line_lower = line.lower()
        
        # Citation indicators
        if any(word in line_lower for word in ['cite', 'cited', 'according to', 'reference']):
            return DependencyType.CITATION
        
        # Reference indicators  
        if any(word in line_lower for word in ['see', 'refer', 'check', 'view']):
            return DependencyType.REFERENCE
        
        # Inclusion indicators
        if any(word in line_lower for word in ['include', 'import', 'load']):
            return DependencyType.INCLUSION
        
        # Default to reference
        return DependencyType.REFERENCE
    
    def _calculate_confidence(self, line: str, referenced_file: str) -> float:
        """Calculate confidence score for the dependency"""
        confidence = 0.5  # Base confidence
        
        line_lower = line.lower()
        
        # Higher confidence for explicit mentions
        if referenced_file.lower() in line_lower:
            confidence += 0.3
        
        # Higher confidence for strong reference words
        strong_words = ['see', 'refer to', 'check', 'cited in', 'according to']
        if any(word in line_lower for word in strong_words):
            confidence += 0.2
        
        # Cap at 1.0
        return min(confidence, 1.0)
    
    async def build_reference_graph(self, document_paths: List[str]) -> ReferenceGraph:
        """Build a graph of document references"""
        self.logger.info(f"Building reference graph for {len(document_paths)} documents")
        
        # Detect all dependencies
        dependencies = await self.detect_dependencies(document_paths)
        
        # Build graph
        graph = ReferenceGraph()
        
        # Add all documents as nodes
        for doc_path in document_paths:
            graph.nodes.add(doc_path)
        
        # Add dependencies as edges
        graph.edges = dependencies
        
        # Build reference chains
        graph.reference_chains = self._find_reference_chains(dependencies)
        
        return graph
    
    def _find_reference_chains(self, dependencies: List[DocumentDependency]) -> List[List[str]]:
        """Find chains of references between documents"""
        # Build networkx graph for analysis
        G = nx.DiGraph()
        
        for dep in dependencies:
            G.add_edge(dep.source_document, dep.target_document)
        
        # Find all simple paths (chains)
        chains = []
        
        # Find paths of length 2-4
        for source in G.nodes():
            for target in G.nodes():
                if source != target:
                    try:
                        # Find all simple paths between source and target
                        paths = list(nx.all_simple_paths(G, source, target, cutoff=4))
                        chains.extend(paths)
                    except:
                        # No path exists
                        continue
        
        return chains


# Temporal document ordering functionality
@dataclass
class TemporalOrder:
    """Temporal ordering of documents"""
    document_path: str
    creation_time: float
    modification_time: float
    temporal_rank: int


class DocumentScheduler:
    """Schedules document processing based on priorities and dependencies"""
    
    def __init__(self):
        """Initialize document scheduler"""
        self.logger = logger
    
    async def create_processing_schedule(self, document_paths: List[str], 
                                       priorities: Optional[Dict[str, int]] = None) -> 'ProcessingSchedule':
        """Create optimal processing schedule"""
        from .multi_document_engine import ProcessingSchedule  # Avoid circular import
        
        # Default priorities if not provided
        if priorities is None:
            priorities = {doc: 5 for doc in document_paths}  # Medium priority
        
        # Sort by priority (higher first)
        processing_order = sorted(document_paths, 
                                key=lambda doc: priorities.get(doc, 0), 
                                reverse=True)
        
        # Calculate estimated time (simplified)
        estimated_time = len(document_paths) * 0.5  # 0.5 seconds per document
        
        # Identify parallel groups (documents with same priority)
        parallel_groups = []
        priority_groups = {}
        
        for doc in document_paths:
            priority = priorities.get(doc, 0)
            if priority not in priority_groups:
                priority_groups[priority] = []
            priority_groups[priority].append(doc)
        
        # Groups with multiple documents can be processed in parallel
        for priority, docs in priority_groups.items():
            if len(docs) > 1:
                parallel_groups.append(docs)
        
        schedule = ProcessingSchedule(
            processing_order=processing_order,
            estimated_total_time=estimated_time,
            parallel_groups=parallel_groups
        )
        
        return schedule
    
    async def sort_documents_temporal(self, document_paths: List[str]) -> List[TemporalOrder]:
        """Sort documents by temporal order"""
        temporal_orders = []
        
        for doc_path in document_paths:
            try:
                import os
                stat = os.stat(doc_path)
                
                temporal_order = TemporalOrder(
                    document_path=doc_path,
                    creation_time=stat.st_ctime,
                    modification_time=stat.st_mtime,
                    temporal_rank=0  # Will be set after sorting
                )
                temporal_orders.append(temporal_order)
                
            except Exception as e:
                self.logger.warning(f"Failed to get temporal info for {doc_path}: {e}")
        
        # Sort by modification time
        temporal_orders.sort(key=lambda x: x.modification_time)
        
        # Assign ranks
        for i, order in enumerate(temporal_orders):
            order.temporal_rank = i + 1
        
        return temporal_orders


@dataclass
class ProcessingSchedule:
    """Document processing schedule"""
    processing_order: List[str]
    estimated_total_time: float
    parallel_groups: List[List[str]] = field(default_factory=list)
    dependencies: List[DocumentDependency] = field(default_factory=list)