"""
Structural Analyzer for document structure analysis
"""

import asyncio
import logging
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum

logger = logging.getLogger(__name__)


@dataclass
class StructuralElement:
    """Structural element found in document"""
    element_type: str  # heading, section, list, table, etc.
    level: int
    content: str
    confidence: float
    position: int


@dataclass
class StructuralPattern:
    """Structural pattern detected in document"""
    pattern_name: str
    pattern_strength: float
    examples: List[str] = field(default_factory=list)
    pattern_type: str = "formatting"  # formatting, academic_paper, etc.
    frequency: int = 1  # How many documents contain this pattern
    
    @property
    def confidence(self) -> float:
        """Confidence score (alias for pattern_strength)"""
        return self.pattern_strength


@dataclass
class DocumentStructureResult:
    """Result of single document structure analysis"""
    headings: List[StructuralElement]
    sections: List[str]
    has_abstract: bool = False
    has_introduction: bool = False
    max_heading_level: int = 0
    structure_type: str = "unknown"

@dataclass
class StructuralPatternResult:
    """Result of structural pattern detection"""
    common_patterns: List[StructuralPattern]
    pattern_frequency: Dict[str, int]
    overall_consistency: float
    pattern_variations: List[str] = field(default_factory=list)
    
    def get_pattern_names(self) -> List[str]:
        """Get names of detected patterns"""
        return [pattern.pattern_name for pattern in self.common_patterns]

@dataclass
class StructuralAnalysisResult:
    """Result of document structure analysis"""
    structural_elements: List[StructuralElement]
    document_hierarchy: Dict[str, Any]
    formatting_patterns: List[StructuralPattern]
    overall_confidence: float


class StructuralAnalyzer:
    """Analyzes document structure including headings, sections, formatting"""
    
    def __init__(self):
        self.logger = logger
        self._structural_patterns = self._build_structural_patterns()
        
    def _build_structural_patterns(self) -> Dict[str, re.Pattern]:
        """Build regex patterns for structural element detection"""
        return {
            "heading": re.compile(r'^#+\s+(.+)$', re.MULTILINE),
            "numbered_list": re.compile(r'^\s*\d+\.\s+(.+)$', re.MULTILINE),
            "bullet_list": re.compile(r'^\s*[-*]\s+(.+)$', re.MULTILINE),
            "bold_text": re.compile(r'\*\*(.+?)\*\*'),
            "italic_text": re.compile(r'\*(.+?)\*'),
            "section_break": re.compile(r'^-{3,}$', re.MULTILINE),
        }

    async def analyze_document_structure(self, documents: List[str]) -> StructuralAnalysisResult:
        """Analyze headings, sections, formatting across documents"""
        all_elements = []
        hierarchies = {}
        patterns = []
        confidence_scores = []
        
        for doc_path in documents:
            try:
                with open(doc_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract structural elements
                elements = self._extract_structural_elements(content)
                all_elements.extend(elements)
                
                # Build document hierarchy
                hierarchy = self._build_document_hierarchy(elements)
                hierarchies[doc_path] = hierarchy
                
                # Detect formatting patterns
                doc_patterns = self._detect_formatting_patterns(content)
                patterns.extend(doc_patterns)
                
                # Calculate confidence
                confidence = self._calculate_structural_confidence(elements)
                confidence_scores.append(confidence)
                
            except Exception as e:
                self.logger.warning(f"Failed to analyze structure in {doc_path}: {e}")
                confidence_scores.append(0.5)
        
        overall_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
        
        return StructuralAnalysisResult(
            structural_elements=all_elements,
            document_hierarchy=hierarchies,
            formatting_patterns=patterns,
            overall_confidence=overall_confidence
        )
    
    def _extract_structural_elements(self, content: str) -> List[StructuralElement]:
        """Extract structural elements from document content"""
        elements = []
        
        # Extract headings
        heading_matches = self._structural_patterns["heading"].finditer(content)
        for match in heading_matches:
            heading_line = match.group(0)
            level = len(heading_line.split()[0])  # Count # symbols
            heading_text = match.group(1)
            
            element = StructuralElement(
                element_type="heading",
                level=level,
                content=heading_text,
                confidence=0.9,
                position=match.start()
            )
            elements.append(element)
        
        # Extract numbered lists
        list_matches = self._structural_patterns["numbered_list"].finditer(content)
        for match in list_matches:
            element = StructuralElement(
                element_type="numbered_list",
                level=1,
                content=match.group(1),
                confidence=0.85,
                position=match.start()
            )
            elements.append(element)
        
        # Extract bullet lists
        bullet_matches = self._structural_patterns["bullet_list"].finditer(content)
        for match in bullet_matches:
            element = StructuralElement(
                element_type="bullet_list",
                level=1,
                content=match.group(1),
                confidence=0.85,
                position=match.start()
            )
            elements.append(element)
        
        return elements
    
    def _build_document_hierarchy(self, elements: List[StructuralElement]) -> Dict[str, Any]:
        """Build hierarchical structure from structural elements"""
        hierarchy = {"type": "document", "children": []}
        current_section = hierarchy
        
        for element in sorted(elements, key=lambda x: x.position):
            if element.element_type == "heading":
                section = {
                    "type": "section",
                    "level": element.level,
                    "title": element.content,
                    "children": []
                }
                current_section["children"].append(section)
                current_section = section
            else:
                current_section["children"].append({
                    "type": element.element_type,
                    "content": element.content
                })
        
        return hierarchy
    
    def _detect_formatting_patterns(self, content: str) -> List[StructuralPattern]:
        """Detect formatting patterns in document"""
        patterns = []
        
        # Check for bold formatting
        bold_matches = self._structural_patterns["bold_text"].findall(content)
        if bold_matches:
            patterns.append(StructuralPattern(
                pattern_name="bold_formatting",
                pattern_strength=min(1.0, len(bold_matches) / 10),
                examples=bold_matches[:3],
                pattern_type="formatting"
            ))
        
        # Check for italic formatting
        italic_matches = self._structural_patterns["italic_text"].findall(content)
        if italic_matches:
            patterns.append(StructuralPattern(
                pattern_name="italic_formatting",
                pattern_strength=min(1.0, len(italic_matches) / 10),
                examples=italic_matches[:3],
                pattern_type="formatting"
            ))
        
        # Check for hierarchical structure
        heading_matches = self._structural_patterns["heading"].findall(content)
        if len(heading_matches) > 3:
            patterns.append(StructuralPattern(
                pattern_name="hierarchical_structure",
                pattern_strength=max(0.75, min(1.0, len(heading_matches) / 10)),  # Boost confidence
                examples=heading_matches[:3],
                pattern_type="structural"
            ))
        
        # Check for academic paper pattern
        content_lower = content.lower()
        academic_markers = ["abstract", "introduction", "methodology", "results", "conclusion", "references"]
        academic_score = sum(1 for marker in academic_markers if marker in content_lower)
        
        if academic_score >= 3:
            patterns.append(StructuralPattern(
                pattern_name="academic_paper",
                pattern_strength=max(0.75, min(1.0, academic_score / 6)),  # Ensure > 0.7
                examples=[marker for marker in academic_markers if marker in content_lower][:3],
                pattern_type="academic_paper"
            ))
        
        return patterns
    
    def _calculate_structural_confidence(self, elements: List[StructuralElement]) -> float:
        """Calculate confidence for structural analysis"""
        if not elements:
            return 0.5
        
        # Higher confidence for more structured documents
        base_confidence = 0.7
        structure_factor = min(1.0, len(elements) / 10)
        
        return min(0.95, base_confidence + 0.2 * structure_factor)
    
    async def analyze_document_structures(self, documents: List[Dict[str, Any]]) -> List[DocumentStructureResult]:
        """Analyze structures of multiple documents"""
        results = []
        
        for doc in documents:
            content = doc.get("content", "")
            self.logger.info(f"Analyzing document content (first 200 chars): {content[:200]!r}")
            
            # Extract structural elements
            elements = self._extract_structural_elements(content)
            self.logger.info(f"Extracted {len(elements)} structural elements")
            
            # Extract headings
            headings = [elem for elem in elements if elem.element_type == "heading"]
            
            # Extract sections
            sections = [elem.content for elem in headings]
            
            # Check for abstract and introduction
            content_lower = content.lower()
            has_abstract = "abstract" in content_lower
            has_introduction = "introduction" in content_lower
            
            # Find max heading level
            max_level = max([h.level for h in headings]) if headings else 0
            
            # Determine structure type
            structure_type = self._determine_structure_type(content, headings)
            
            result = DocumentStructureResult(
                headings=headings,
                sections=sections,
                has_abstract=has_abstract,
                has_introduction=has_introduction,
                max_heading_level=max_level,
                structure_type=structure_type
            )
            results.append(result)
        
        return results
    
    def _determine_structure_type(self, content: str, headings: List[StructuralElement]) -> str:
        """Determine the structure type of document"""
        content_lower = content.lower()
        heading_texts = [h.content.lower() for h in headings]
        
        # Check for academic paper patterns
        academic_markers = ["abstract", "introduction", "methodology", "results", "conclusion", "references"]
        academic_score = sum(1 for marker in academic_markers if any(marker in h for h in heading_texts))
        
        if academic_score >= 3:
            return "academic_paper"
        elif "experiment" in content_lower or "data" in content_lower:
            return "data_document"
        elif "review" in content_lower or "overview" in content_lower:
            return "review_article"
        else:
            return "unknown"
    
    async def detect_structural_patterns(self, documents: List[Dict[str, Any]]) -> StructuralPatternResult:
        """Detect structural patterns across documents"""
        all_patterns = []
        pattern_counts = {}
        
        for doc in documents:
            try:
                content = doc.get("content", "")
                patterns = self._detect_formatting_patterns(content)
                all_patterns.extend(patterns)
                
                # Count pattern occurrences
                for pattern in patterns:
                    if pattern.pattern_name not in pattern_counts:
                        pattern_counts[pattern.pattern_name] = 0
                    pattern_counts[pattern.pattern_name] += 1
                
            except Exception as e:
                self.logger.warning(f"Failed to detect patterns in {doc}: {e}")
        
        # Find common patterns (appearing in multiple documents OR high strength)
        common_patterns = []
        for pattern in all_patterns:
            # Include if appears multiple times OR has high strength (important pattern)
            is_common = (pattern_counts[pattern.pattern_name] > 1 or 
                        pattern.pattern_strength > 0.7 or 
                        pattern.pattern_type == "academic_paper")
            
            if is_common:
                # Only add if not already added
                if not any(p.pattern_name == pattern.pattern_name for p in common_patterns):
                    # Set the frequency from our counts
                    pattern.frequency = pattern_counts[pattern.pattern_name]
                    common_patterns.append(pattern)
        
        # Calculate overall consistency
        total_docs = len(documents)
        avg_pattern_frequency = sum(pattern_counts.values()) / len(pattern_counts) if pattern_counts else 0
        overall_consistency = min(1.0, avg_pattern_frequency / total_docs)
        
        # Generate pattern variations (different ways patterns appear)
        pattern_variations = []
        for pattern in all_patterns:
            if pattern.examples:
                for example in pattern.examples:
                    if example not in pattern_variations:
                        pattern_variations.append(example)
        
        return StructuralPatternResult(
            common_patterns=common_patterns,
            pattern_frequency=pattern_counts,
            overall_consistency=overall_consistency,
            pattern_variations=pattern_variations
        )