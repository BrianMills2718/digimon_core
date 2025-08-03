#!/usr/bin/env python3
"""
Research Results Export System

Provides comprehensive export capabilities for research results, including LaTeX documents,
BibTeX citations, academic reports, and various publication formats. Supports entity profiles,
relationship networks, analysis results, and formatted bibliographies for academic publishing.
"""

import logging
import json
import re
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum
import xml.etree.ElementTree as ET
from collections import defaultdict, Counter
import tempfile
import subprocess
import shutil

logger = logging.getLogger(__name__)


class ExportFormat(Enum):
    """Supported export formats"""
    LATEX_ARTICLE = "latex_article"
    LATEX_REPORT = "latex_report"
    LATEX_BOOK = "latex_book"
    BIBTEX = "bibtex"
    ENDNOTE = "endnote"
    RIS = "ris"
    JSON_ACADEMIC = "json_academic"
    XML_TEI = "xml_tei"
    MARKDOWN_ACADEMIC = "markdown_academic"
    HTML_REPORT = "html_report"
    CSV_DATA = "csv_data"
    GEPHI_GRAPH = "gephi_graph"


class CitationStyle(Enum):
    """Academic citation styles"""
    APA = "apa"
    MLA = "mla"
    CHICAGO = "chicago"
    IEEE = "ieee"
    NATURE = "nature"
    HARVARD = "harvard"
    VANCOUVER = "vancouver"


@dataclass
class EntityProfile:
    """Consolidated entity profile for export"""
    entity_id: str
    canonical_name: str
    entity_type: str
    aliases: List[str] = field(default_factory=list)
    attributes: Dict[str, Any] = field(default_factory=dict)
    confidence_score: float = 0.0
    source_documents: List[str] = field(default_factory=list)
    relationships: List[Dict[str, Any]] = field(default_factory=list)
    mentions: List[Dict[str, Any]] = field(default_factory=list)
    provenance: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ResearchDocument:
    """Research document metadata"""
    document_id: str
    title: str
    authors: List[str] = field(default_factory=list)
    publication_year: Optional[int] = None
    journal: Optional[str] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    abstract: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    document_type: str = "article"
    source_file: Optional[str] = None
    processing_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnalysisResult:
    """Analysis result for export"""
    analysis_id: str
    analysis_type: str
    title: str
    description: str
    results: Dict[str, Any] = field(default_factory=dict)
    entities_involved: List[str] = field(default_factory=list)
    confidence_metrics: Dict[str, float] = field(default_factory=dict)
    methodology: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ExportConfiguration:
    """Configuration for export operations"""
    format: ExportFormat
    output_path: str
    citation_style: CitationStyle = CitationStyle.APA
    include_bibliography: bool = True
    include_entity_profiles: bool = True
    include_relationship_network: bool = True
    include_analysis_results: bool = True
    include_provenance: bool = False
    max_entities: Optional[int] = None
    entity_types_filter: Optional[List[str]] = None
    confidence_threshold: float = 0.5
    template_path: Optional[str] = None
    custom_metadata: Dict[str, Any] = field(default_factory=dict)


class ExportTemplate(ABC):
    """Abstract base class for export templates"""
    
    @abstractmethod
    def generate_content(self, data: Dict[str, Any], config: ExportConfiguration) -> str:
        """Generate formatted content from data"""
        pass
    
    @abstractmethod
    def get_file_extension(self) -> str:
        """Get appropriate file extension"""
        pass


class LaTeXTemplate(ExportTemplate):
    """LaTeX document template generator"""
    
    def __init__(self, document_class: str = "article"):
        self.document_class = document_class
        self.packages = [
            "inputenc", "fontenc", "babel", "amsmath", "amsfonts", 
            "amssymb", "graphicx", "hyperref", "natbib", "booktabs",
            "longtable", "array", "multirow", "xcolor", "tikz"
        ]
    
    def generate_content(self, data: Dict[str, Any], config: ExportConfiguration) -> str:
        """Generate LaTeX document content"""
        content = []
        
        # Document class and packages
        content.append(f"\\documentclass[12pt,a4paper]{{{self.document_class}}}")
        content.append("")
        
        # Package imports
        for package in self.packages:
            if package == "babel":
                content.append("\\usepackage[english]{babel}")
            elif package == "inputenc":
                content.append("\\usepackage[utf8]{inputenc}")
            elif package == "fontenc":
                content.append("\\usepackage[T1]{fontenc}")
            else:
                content.append(f"\\usepackage{{{package}}}")
        
        content.append("")
        content.append("% Custom commands")
        content.append("\\newcommand{\\entityref}[1]{\\textbf{#1}}")
        content.append("\\newcommand{\\confidence}[1]{\\textit{(confidence: #1)}}")
        content.append("")
        
        # Document metadata
        title = data.get('title', 'Research Analysis Results')
        author = data.get('author', 'KGAS Research System')
        date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
        
        content.append(f"\\title{{{self._escape_latex(title)}}}")
        content.append(f"\\author{{{self._escape_latex(author)}}}")
        content.append(f"\\date{{{date}}}")
        content.append("")
        
        # Begin document
        content.append("\\begin{document}")
        content.append("\\maketitle")
        content.append("")
        
        # Table of contents
        if self.document_class in ["report", "book"]:
            content.append("\\tableofcontents")
            content.append("\\newpage")
            content.append("")
        
        # Abstract
        if 'abstract' in data:
            content.append("\\begin{abstract}")
            content.append(self._escape_latex(data['abstract']))
            content.append("\\end{abstract}")
            content.append("")
        
        # Main content sections
        content.extend(self._generate_introduction(data))
        content.extend(self._generate_methodology_section(data))
        content.extend(self._generate_entity_profiles_section(data, config))
        content.extend(self._generate_relationship_analysis_section(data, config))
        content.extend(self._generate_analysis_results_section(data, config))
        content.extend(self._generate_conclusions_section(data))
        
        # Bibliography
        if config.include_bibliography and 'bibliography' in data:
            content.extend(self._generate_bibliography_section(data, config))
        
        # Appendices
        if config.include_provenance and 'provenance' in data:
            content.extend(self._generate_provenance_appendix(data))
        
        content.append("\\end{document}")
        
        return "\n".join(content)
    
    def get_file_extension(self) -> str:
        return ".tex"
    
    def _escape_latex(self, text: str) -> str:
        """Escape special LaTeX characters"""
        if not text:
            return ""
        
        # LaTeX special characters
        replacements = {
            '\\': '\\textbackslash{}',
            '{': '\\{',
            '}': '\\}',
            '$': '\\$',
            '&': '\\&',
            '%': '\\%',
            '#': '\\#',
            '^': '\\textasciicircum{}',
            '_': '\\_',
            '~': '\\textasciitilde{}',
        }
        
        for char, replacement in replacements.items():
            text = text.replace(char, replacement)
        
        return text
    
    def _generate_introduction(self, data: Dict[str, Any]) -> List[str]:
        """Generate introduction section"""
        content = []
        content.append("\\section{Introduction}")
        content.append("")
        
        intro_text = data.get('introduction', 
            "This report presents the results of automated research analysis conducted using "
            "the KGAS (Knowledge Graph Analysis System). The analysis includes entity "
            "extraction, relationship discovery, and comprehensive network analysis of "
            "the processed documents."
        )
        
        content.append(self._escape_latex(intro_text))
        content.append("")
        
        # Document statistics
        if 'document_stats' in data:
            stats = data['document_stats']
            content.append("\\subsection{Document Collection Overview}")
            content.append("\\begin{itemize}")
            content.append(f"\\item Total documents processed: {stats.get('total_documents', 'N/A')}")
            content.append(f"\\item Total entities extracted: {stats.get('total_entities', 'N/A')}")
            content.append(f"\\item Total relationships identified: {stats.get('total_relationships', 'N/A')}")
            content.append(f"\\item Analysis completion date: {stats.get('completion_date', 'N/A')}")
            content.append("\\end{itemize}")
            content.append("")
        
        return content
    
    def _generate_methodology_section(self, data: Dict[str, Any]) -> List[str]:
        """Generate methodology section"""
        content = []
        content.append("\\section{Methodology}")
        content.append("")
        
        methodology = data.get('methodology', {})
        
        # Entity extraction methodology
        content.append("\\subsection{Entity Extraction}")
        entity_method = methodology.get('entity_extraction', 
            "Named Entity Recognition (NER) was performed using advanced natural language "
            "processing techniques, including statistical models and rule-based approaches."
        )
        content.append(self._escape_latex(entity_method))
        content.append("")
        
        # Relationship extraction methodology
        content.append("\\subsection{Relationship Extraction}")
        relation_method = methodology.get('relationship_extraction',
            "Relationships between entities were identified using dependency parsing, "
            "semantic role labeling, and pattern matching techniques."
        )
        content.append(self._escape_latex(relation_method))
        content.append("")
        
        # Quality assessment methodology
        content.append("\\subsection{Quality Assessment}")
        quality_method = methodology.get('quality_assessment',
            "Confidence scores were computed based on extraction frequency, source "
            "reliability, and cross-validation across multiple documents."
        )
        content.append(self._escape_latex(quality_method))
        content.append("")
        
        return content
    
    def _generate_entity_profiles_section(self, data: Dict[str, Any], 
                                        config: ExportConfiguration) -> List[str]:
        """Generate entity profiles section"""
        if not config.include_entity_profiles or 'entities' not in data:
            return []
        
        content = []
        content.append("\\section{Entity Profiles}")
        content.append("")
        
        entities = data['entities']
        if config.max_entities:
            entities = entities[:config.max_entities]
        
        # Filter by confidence threshold
        entities = [e for e in entities if e.get('confidence_score', 0) >= config.confidence_threshold]
        
        # Filter by entity types
        if config.entity_types_filter:
            entities = [e for e in entities if e.get('entity_type') in config.entity_types_filter]
        
        content.append(f"This section presents detailed profiles for {len(entities)} entities "
                      f"meeting the specified criteria (confidence ≥ {config.confidence_threshold}).")
        content.append("")
        
        # Group entities by type
        entities_by_type = defaultdict(list)
        for entity in entities:
            entity_type = entity.get('entity_type', 'Unknown')
            entities_by_type[entity_type].append(entity)
        
        for entity_type, type_entities in sorted(entities_by_type.items()):
            content.append(f"\\subsection{{{self._escape_latex(entity_type)} Entities}}")
            content.append("")
            
            for entity in type_entities:
                content.extend(self._generate_entity_profile_subsection(entity))
        
        return content
    
    def _generate_entity_profile_subsection(self, entity: Dict[str, Any]) -> List[str]:
        """Generate individual entity profile subsection"""
        content = []
        
        name = entity.get('canonical_name', entity.get('entity_id', 'Unknown'))
        content.append(f"\\subsubsection{{{self._escape_latex(name)}}}")
        content.append("")
        
        # Basic information table
        content.append("\\begin{table}[h]")
        content.append("\\centering")
        content.append("\\begin{tabular}{|l|l|}")
        content.append("\\hline")
        content.append("\\textbf{Property} & \\textbf{Value} \\\\")
        content.append("\\hline")
        
        # Entity details
        content.append(f"Entity ID & {self._escape_latex(entity.get('entity_id', 'N/A'))} \\\\")
        content.append("\\hline")
        content.append(f"Type & {self._escape_latex(entity.get('entity_type', 'N/A'))} \\\\")
        content.append("\\hline")
        content.append(f"Confidence & {entity.get('confidence_score', 0):.3f} \\\\")
        content.append("\\hline")
        
        # Aliases
        aliases = entity.get('aliases', [])
        if aliases:
            aliases_str = ", ".join(aliases[:5])  # Limit to first 5 aliases
            if len(aliases) > 5:
                aliases_str += f" (+{len(aliases) - 5} more)"
            content.append(f"Aliases & {self._escape_latex(aliases_str)} \\\\")
            content.append("\\hline")
        
        # Source documents count
        source_docs = entity.get('source_documents', [])
        content.append(f"Source Documents & {len(source_docs)} \\\\")
        content.append("\\hline")
        
        # Mentions count
        mentions = entity.get('mentions', [])
        content.append(f"Total Mentions & {len(mentions)} \\\\")
        content.append("\\hline")
        
        content.append("\\end{tabular}")
        content.append(f"\\caption{{Profile for entity: {self._escape_latex(name)}}}")
        content.append("\\end{table}")
        content.append("")
        
        # Key attributes
        attributes = entity.get('attributes', {})
        if attributes:
            content.append("\\paragraph{Key Attributes}")
            content.append("\\begin{itemize}")
            for key, value in list(attributes.items())[:10]:  # Limit to 10 attributes
                content.append(f"\\item \\textbf{{{self._escape_latex(key)}}}: {self._escape_latex(str(value))}")
            content.append("\\end{itemize}")
            content.append("")
        
        # Top relationships
        relationships = entity.get('relationships', [])
        if relationships:
            content.append("\\paragraph{Key Relationships}")
            content.append("\\begin{itemize}")
            for rel in relationships[:5]:  # Show top 5 relationships
                rel_type = rel.get('relationship_type', 'unknown')
                target = rel.get('target_entity', 'unknown')
                confidence = rel.get('confidence', 0)
                content.append(f"\\item \\textbf{{{self._escape_latex(rel_type)}}}: "
                             f"{self._escape_latex(target)} \\confidence{{{confidence:.2f}}}")
            content.append("\\end{itemize}")
            content.append("")
        
        return content
    
    def _generate_relationship_analysis_section(self, data: Dict[str, Any], 
                                              config: ExportConfiguration) -> List[str]:
        """Generate relationship network analysis section"""
        if not config.include_relationship_network or 'relationships' not in data:
            return []
        
        content = []
        content.append("\\section{Relationship Network Analysis}")
        content.append("")
        
        relationships = data['relationships']
        
        # Network statistics
        content.append("\\subsection{Network Statistics}")
        network_stats = data.get('network_stats', {})
        
        content.append("\\begin{table}[h]")
        content.append("\\centering")
        content.append("\\begin{tabular}{|l|r|}")
        content.append("\\hline")
        content.append("\\textbf{Metric} & \\textbf{Value} \\\\")
        content.append("\\hline")
        content.append(f"Total Relationships & {len(relationships)} \\\\")
        content.append("\\hline")
        content.append(f"Unique Entities & {network_stats.get('unique_entities', 'N/A')} \\\\")
        content.append("\\hline")
        content.append(f"Average Degree & {network_stats.get('average_degree', 'N/A'):.2f} \\\\")
        content.append("\\hline")
        content.append(f"Network Density & {network_stats.get('density', 'N/A'):.4f} \\\\")
        content.append("\\hline")
        content.append(f"Connected Components & {network_stats.get('components', 'N/A')} \\\\")
        content.append("\\hline")
        content.append("\\end{tabular}")
        content.append("\\caption{Network topology statistics}")
        content.append("\\end{table}")
        content.append("")
        
        # Relationship type distribution
        content.append("\\subsection{Relationship Type Distribution}")
        rel_types = Counter(rel.get('relationship_type', 'unknown') for rel in relationships)
        
        content.append("\\begin{table}[h]")
        content.append("\\centering")
        content.append("\\begin{tabular}{|l|r|r|}")
        content.append("\\hline")
        content.append("\\textbf{Relationship Type} & \\textbf{Count} & \\textbf{Percentage} \\\\")
        content.append("\\hline")
        
        total_rels = len(relationships)
        for rel_type, count in rel_types.most_common(15):  # Top 15 relationship types
            percentage = (count / total_rels) * 100
            content.append(f"{self._escape_latex(rel_type)} & {count} & {percentage:.1f}\\% \\\\")
            content.append("\\hline")
        
        content.append("\\end{tabular}")
        content.append("\\caption{Distribution of relationship types}")
        content.append("\\end{table}")
        content.append("")
        
        return content
    
    def _generate_analysis_results_section(self, data: Dict[str, Any], 
                                         config: ExportConfiguration) -> List[str]:
        """Generate analysis results section"""
        if not config.include_analysis_results or 'analysis_results' not in data:
            return []
        
        content = []
        content.append("\\section{Analysis Results}")
        content.append("")
        
        analysis_results = data['analysis_results']
        
        for analysis in analysis_results:
            content.extend(self._generate_analysis_result_subsection(analysis))
        
        return content
    
    def _generate_analysis_result_subsection(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate individual analysis result subsection"""
        content = []
        
        title = analysis.get('title', 'Analysis Result')
        content.append(f"\\subsection{{{self._escape_latex(title)}}}")
        content.append("")
        
        # Description
        description = analysis.get('description', '')
        if description:
            content.append(self._escape_latex(description))
            content.append("")
        
        # Methodology
        methodology = analysis.get('methodology', '')
        if methodology:
            content.append("\\paragraph{Methodology}")
            content.append(self._escape_latex(methodology))
            content.append("")
        
        # Results
        results = analysis.get('results', {})
        if results:
            content.append("\\paragraph{Results}")
            
            # Handle different result types
            if isinstance(results, dict):
                content.append("\\begin{itemize}")
                for key, value in results.items():
                    content.append(f"\\item \\textbf{{{self._escape_latex(key)}}}: {self._escape_latex(str(value))}")
                content.append("\\end{itemize}")
            else:
                content.append(self._escape_latex(str(results)))
            
            content.append("")
        
        # Confidence metrics
        confidence_metrics = analysis.get('confidence_metrics', {})
        if confidence_metrics:
            content.append("\\paragraph{Confidence Metrics}")
            content.append("\\begin{itemize}")
            for metric, value in confidence_metrics.items():
                content.append(f"\\item \\textbf{{{self._escape_latex(metric)}}}: {value:.3f}")
            content.append("\\end{itemize}")
            content.append("")
        
        return content
    
    def _generate_conclusions_section(self, data: Dict[str, Any]) -> List[str]:
        """Generate conclusions section"""
        content = []
        content.append("\\section{Conclusions}")
        content.append("")
        
        conclusions = data.get('conclusions', 
            "The analysis successfully extracted and analyzed entities and relationships "
            "from the document collection, providing insights into the structure and "
            "content of the research corpus."
        )
        
        content.append(self._escape_latex(conclusions))
        content.append("")
        
        # Key findings
        key_findings = data.get('key_findings', [])
        if key_findings:
            content.append("\\subsection{Key Findings}")
            content.append("\\begin{enumerate}")
            for finding in key_findings:
                content.append(f"\\item {self._escape_latex(finding)}")
            content.append("\\end{enumerate}")
            content.append("")
        
        # Future work
        future_work = data.get('future_work', [])
        if future_work:
            content.append("\\subsection{Future Work}")
            content.append("\\begin{itemize}")
            for work in future_work:
                content.append(f"\\item {self._escape_latex(work)}")
            content.append("\\end{itemize}")
            content.append("")
        
        return content
    
    def _generate_bibliography_section(self, data: Dict[str, Any], 
                                     config: ExportConfiguration) -> List[str]:
        """Generate bibliography section"""
        content = []
        content.append("\\bibliographystyle{" + config.citation_style.value + "}")
        content.append("\\bibliography{references}")
        content.append("")
        
        return content
    
    def _generate_provenance_appendix(self, data: Dict[str, Any]) -> List[str]:
        """Generate provenance information appendix"""
        content = []
        content.append("\\appendix")
        content.append("\\section{Provenance Information}")
        content.append("")
        
        provenance = data.get('provenance', {})
        
        # Processing history
        processing_history = provenance.get('processing_history', [])
        if processing_history:
            content.append("\\subsection{Processing History}")
            content.append("\\begin{enumerate}")
            for step in processing_history:
                timestamp = step.get('timestamp', 'Unknown')
                operation = step.get('operation', 'Unknown')
                details = step.get('details', '')
                content.append(f"\\item \\textbf{{{timestamp}}}: {self._escape_latex(operation)}")
                if details:
                    content.append(f"\\\\{self._escape_latex(details)}")
            content.append("\\end{enumerate}")
            content.append("")
        
        # System configuration
        system_config = provenance.get('system_configuration', {})
        if system_config:
            content.append("\\subsection{System Configuration}")
            content.append("\\begin{itemize}")
            for key, value in system_config.items():
                content.append(f"\\item \\textbf{{{self._escape_latex(key)}}}: {self._escape_latex(str(value))}")
            content.append("\\end{itemize}")
            content.append("")
        
        return content


class BibTeXTemplate(ExportTemplate):
    """BibTeX bibliography template generator"""
    
    def generate_content(self, data: Dict[str, Any], config: ExportConfiguration) -> str:
        """Generate BibTeX content"""
        content = []
        content.append("% BibTeX bibliography generated by KGAS Research Export System")
        content.append(f"% Generated on: {datetime.now().isoformat()}")
        content.append("")
        
        documents = data.get('documents', [])
        
        for doc in documents:
            content.extend(self._generate_bibtex_entry(doc))
            content.append("")
        
        return "\n".join(content)
    
    def get_file_extension(self) -> str:
        return ".bib"
    
    def _generate_bibtex_entry(self, document: Dict[str, Any]) -> List[str]:
        """Generate individual BibTeX entry"""
        entry_type = self._determine_entry_type(document)
        cite_key = self._generate_cite_key(document)
        
        content = []
        content.append(f"@{entry_type}{{{cite_key},")
        
        # Required and optional fields
        fields = []
        
        # Title
        title = document.get('title', '')
        if title:
            fields.append(f"  title = {{{title}}}")
        
        # Authors
        authors = document.get('authors', [])
        if authors:
            author_str = " and ".join(authors)
            fields.append(f"  author = {{{author_str}}}")
        
        # Year
        year = document.get('publication_year')
        if year:
            fields.append(f"  year = {{{year}}}")
        
        # Journal
        journal = document.get('journal')
        if journal:
            fields.append(f"  journal = {{{journal}}}")
        
        # DOI
        doi = document.get('doi')
        if doi:
            fields.append(f"  doi = {{{doi}}}")
        
        # URL
        url = document.get('url')
        if url:
            fields.append(f"  url = {{{url}}}")
        
        # Abstract
        abstract = document.get('abstract')
        if abstract:
            # Truncate abstract if too long
            if len(abstract) > 500:
                abstract = abstract[:497] + "..."
            fields.append(f"  abstract = {{{abstract}}}")
        
        # Keywords
        keywords = document.get('keywords', [])
        if keywords:
            keyword_str = ", ".join(keywords)
            fields.append(f"  keywords = {{{keyword_str}}}")
        
        # Add fields to content
        content.extend(fields)
        content.append("}")
        
        return content
    
    def _determine_entry_type(self, document: Dict[str, Any]) -> str:
        """Determine appropriate BibTeX entry type"""
        doc_type = document.get('document_type', 'article').lower()
        
        type_mapping = {
            'article': 'article',
            'book': 'book',
            'conference': 'inproceedings',
            'thesis': 'phdthesis',
            'report': 'techreport',
            'webpage': 'misc'
        }
        
        return type_mapping.get(doc_type, 'misc')
    
    def _generate_cite_key(self, document: Dict[str, Any]) -> str:
        """Generate citation key for document"""
        authors = document.get('authors', [])
        year = document.get('publication_year', '')
        title = document.get('title', '')
        
        # Use first author's last name
        if authors:
            first_author = authors[0].split()[-1].lower()  # Last name
            first_author = re.sub(r'[^a-z0-9]', '', first_author)  # Clean
        else:
            first_author = "unknown"
        
        # Use first significant word from title
        if title:
            title_words = re.findall(r'\b[a-zA-Z]{4,}\b', title)
            title_word = title_words[0].lower() if title_words else "title"
        else:
            title_word = "untitled"
        
        # Combine components
        cite_key = f"{first_author}{year}{title_word}"
        
        # Ensure uniqueness by adding document ID if needed
        doc_id = document.get('document_id', '')
        if doc_id:
            cite_key += f"_{doc_id[:8]}"
        
        return cite_key


class JSONAcademicTemplate(ExportTemplate):
    """JSON academic format template"""
    
    def generate_content(self, data: Dict[str, Any], config: ExportConfiguration) -> str:
        """Generate JSON academic format content"""
        export_data = {
            "metadata": {
                "format": "json_academic",
                "version": "1.0",
                "generated_at": datetime.now().isoformat(),
                "generator": "KGAS Research Export System",
                "configuration": {
                    "citation_style": config.citation_style.value,
                    "confidence_threshold": config.confidence_threshold,
                    "include_bibliography": config.include_bibliography,
                    "include_entity_profiles": config.include_entity_profiles,
                    "include_relationship_network": config.include_relationship_network,
                    "include_analysis_results": config.include_analysis_results
                }
            },
            "research_data": {}
        }
        
        # Copy relevant data sections
        if config.include_entity_profiles and 'entities' in data:
            export_data["research_data"]["entities"] = data['entities']
        
        if config.include_relationship_network and 'relationships' in data:
            export_data["research_data"]["relationships"] = data['relationships']
            export_data["research_data"]["network_statistics"] = data.get('network_stats', {})
        
        if config.include_analysis_results and 'analysis_results' in data:
            export_data["research_data"]["analysis_results"] = data['analysis_results']
        
        if config.include_bibliography and 'documents' in data:
            export_data["research_data"]["bibliography"] = data['documents']
        
        # Add summary statistics
        export_data["research_data"]["summary"] = {
            "total_entities": len(data.get('entities', [])),
            "total_relationships": len(data.get('relationships', [])),
            "total_documents": len(data.get('documents', [])),
            "total_analysis_results": len(data.get('analysis_results', []))
        }
        
        return json.dumps(export_data, indent=2, ensure_ascii=False, default=str)
    
    def get_file_extension(self) -> str:
        return ".json"


class ResearchExporter:
    """Main research results export system"""
    
    def __init__(self):
        self.templates = {
            ExportFormat.LATEX_ARTICLE: LaTeXTemplate("article"),
            ExportFormat.LATEX_REPORT: LaTeXTemplate("report"),
            ExportFormat.LATEX_BOOK: LaTeXTemplate("book"),
            ExportFormat.BIBTEX: BibTeXTemplate(),
            ExportFormat.JSON_ACADEMIC: JSONAcademicTemplate()
        }
        
        # Statistics
        self.export_stats = {
            'total_exports': 0,
            'successful_exports': 0,
            'failed_exports': 0,
            'formats_used': Counter(),
            'export_history': []
        }
    
    def export_research_results(self, 
                               entities: List[EntityProfile],
                               documents: List[ResearchDocument],
                               relationships: List[Dict[str, Any]],
                               analysis_results: List[AnalysisResult],
                               config: ExportConfiguration) -> bool:
        """Export research results in specified format"""
        try:
            logger.info(f"Starting export to {config.format.value} format")
            self.export_stats['total_exports'] += 1
            
            # Prepare data for export
            export_data = self._prepare_export_data(
                entities, documents, relationships, analysis_results, config
            )
            
            # Get appropriate template
            template = self.templates.get(config.format)
            if not template:
                raise ValueError(f"Unsupported export format: {config.format}")
            
            # Generate content
            content = template.generate_content(export_data, config)
            
            # Write to file
            output_path = Path(config.output_path)
            if not output_path.suffix:
                output_path = output_path.with_suffix(template.get_file_extension())
            
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Generate additional files if needed
            self._generate_additional_files(export_data, config, output_path)
            
            # Update statistics
            self.export_stats['successful_exports'] += 1
            self.export_stats['formats_used'][config.format.value] += 1
            self.export_stats['export_history'].append({
                'timestamp': datetime.now().isoformat(),
                'format': config.format.value,
                'output_path': str(output_path),
                'entity_count': len(entities),
                'document_count': len(documents),
                'relationship_count': len(relationships),
                'analysis_count': len(analysis_results)
            })
            
            logger.info(f"Export completed successfully: {output_path}")
            return True
            
        except Exception as e:
            self.export_stats['failed_exports'] += 1
            logger.error(f"Export failed: {e}", exc_info=True)
            return False
    
    def _prepare_export_data(self, 
                           entities: List[EntityProfile],
                           documents: List[ResearchDocument],
                           relationships: List[Dict[str, Any]],
                           analysis_results: List[AnalysisResult],
                           config: ExportConfiguration) -> Dict[str, Any]:
        """Prepare data for export"""
        
        # Filter entities by confidence threshold
        filtered_entities = [
            e for e in entities 
            if e.confidence_score >= config.confidence_threshold
        ]
        
        # Filter by entity types if specified
        if config.entity_types_filter:
            filtered_entities = [
                e for e in filtered_entities 
                if e.entity_type in config.entity_types_filter
            ]
        
        # Limit entities if specified
        if config.max_entities:
            filtered_entities = filtered_entities[:config.max_entities]
        
        # Convert to dictionaries for template processing
        entity_dicts = [self._entity_profile_to_dict(e) for e in filtered_entities]
        document_dicts = [self._document_to_dict(d) for d in documents]
        analysis_dicts = [self._analysis_result_to_dict(a) for a in analysis_results]
        
        # Calculate network statistics
        network_stats = self._calculate_network_statistics(relationships, filtered_entities)
        
        export_data = {
            'title': config.custom_metadata.get('title', 'Research Analysis Results'),
            'author': config.custom_metadata.get('author', 'KGAS Research System'),
            'date': datetime.now().strftime('%Y-%m-%d'),
            'abstract': config.custom_metadata.get('abstract'),
            'introduction': config.custom_metadata.get('introduction'),
            'methodology': config.custom_metadata.get('methodology', {}),
            'conclusions': config.custom_metadata.get('conclusions'),
            'key_findings': config.custom_metadata.get('key_findings', []),
            'future_work': config.custom_metadata.get('future_work', []),
            'entities': entity_dicts,
            'documents': document_dicts,
            'relationships': relationships,
            'analysis_results': analysis_dicts,
            'network_stats': network_stats,
            'document_stats': {
                'total_documents': len(documents),
                'total_entities': len(filtered_entities),
                'total_relationships': len(relationships),
                'completion_date': datetime.now().strftime('%Y-%m-%d')
            }
        }
        
        return export_data
    
    def _entity_profile_to_dict(self, entity: EntityProfile) -> Dict[str, Any]:
        """Convert EntityProfile to dictionary"""
        return {
            'entity_id': entity.entity_id,
            'canonical_name': entity.canonical_name,
            'entity_type': entity.entity_type,
            'aliases': entity.aliases,
            'attributes': entity.attributes,
            'confidence_score': entity.confidence_score,
            'source_documents': entity.source_documents,
            'relationships': entity.relationships,
            'mentions': entity.mentions,
            'provenance': entity.provenance,
            'created_at': entity.created_at
        }
    
    def _document_to_dict(self, document: ResearchDocument) -> Dict[str, Any]:
        """Convert ResearchDocument to dictionary"""
        return {
            'document_id': document.document_id,
            'title': document.title,
            'authors': document.authors,
            'publication_year': document.publication_year,
            'journal': document.journal,
            'doi': document.doi,
            'url': document.url,
            'abstract': document.abstract,
            'keywords': document.keywords,
            'document_type': document.document_type,
            'source_file': document.source_file,
            'processing_metadata': document.processing_metadata
        }
    
    def _analysis_result_to_dict(self, analysis: AnalysisResult) -> Dict[str, Any]:
        """Convert AnalysisResult to dictionary"""
        return {
            'analysis_id': analysis.analysis_id,
            'analysis_type': analysis.analysis_type,
            'title': analysis.title,
            'description': analysis.description,
            'results': analysis.results,
            'entities_involved': analysis.entities_involved,
            'confidence_metrics': analysis.confidence_metrics,
            'methodology': analysis.methodology,
            'timestamp': analysis.timestamp
        }
    
    def _calculate_network_statistics(self, relationships: List[Dict[str, Any]], 
                                    entities: List[EntityProfile]) -> Dict[str, Any]:
        """Calculate network topology statistics"""
        if not relationships or not entities:
            return {}
        
        # Build entity set
        entity_ids = {e.entity_id for e in entities}
        
        # Count unique entities in relationships
        rel_entities = set()
        for rel in relationships:
            source = rel.get('source_entity')
            target = rel.get('target_entity')
            if source:
                rel_entities.add(source)
            if target:
                rel_entities.add(target)
        
        # Calculate degree distribution
        degree_count = Counter()
        for rel in relationships:
            source = rel.get('source_entity')
            target = rel.get('target_entity')
            if source:
                degree_count[source] += 1
            if target:
                degree_count[target] += 1
        
        # Calculate statistics
        unique_entities = len(rel_entities)
        total_relationships = len(relationships)
        
        avg_degree = sum(degree_count.values()) / max(1, len(degree_count))
        max_possible_edges = unique_entities * (unique_entities - 1) / 2
        density = total_relationships / max(1, max_possible_edges)
        
        return {
            'unique_entities': unique_entities,
            'total_relationships': total_relationships,
            'average_degree': avg_degree,
            'max_degree': max(degree_count.values()) if degree_count else 0,
            'density': density,
            'components': 1  # Simplified - would need graph analysis for accurate count
        }
    
    def _generate_additional_files(self, export_data: Dict[str, Any], 
                                 config: ExportConfiguration, 
                                 main_output_path: Path) -> None:
        """Generate additional supporting files"""
        
        # Generate BibTeX file for LaTeX exports
        if config.format in [ExportFormat.LATEX_ARTICLE, ExportFormat.LATEX_REPORT, ExportFormat.LATEX_BOOK]:
            if config.include_bibliography and 'documents' in export_data:
                bib_template = BibTeXTemplate()
                bib_content = bib_template.generate_content(export_data, config)
                
                bib_path = main_output_path.with_suffix('.bib')
                with open(bib_path, 'w', encoding='utf-8') as f:
                    f.write(bib_content)
                
                logger.info(f"Generated bibliography file: {bib_path}")
        
        # Generate CSV data export for analysis
        if export_data.get('entities'):
            self._generate_entity_csv(export_data['entities'], main_output_path)
        
        if export_data.get('relationships'):
            self._generate_relationship_csv(export_data['relationships'], main_output_path)
    
    def _generate_entity_csv(self, entities: List[Dict[str, Any]], base_path: Path) -> None:
        """Generate CSV file with entity data"""
        csv_path = base_path.with_name(f"{base_path.stem}_entities.csv")
        
        try:
            import csv
            
            with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['entity_id', 'canonical_name', 'entity_type', 'confidence_score', 
                            'aliases_count', 'mentions_count', 'source_documents_count']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for entity in entities:
                    writer.writerow({
                        'entity_id': entity.get('entity_id', ''),
                        'canonical_name': entity.get('canonical_name', ''),
                        'entity_type': entity.get('entity_type', ''),
                        'confidence_score': entity.get('confidence_score', 0),
                        'aliases_count': len(entity.get('aliases', [])),
                        'mentions_count': len(entity.get('mentions', [])),
                        'source_documents_count': len(entity.get('source_documents', []))
                    })
            
            logger.info(f"Generated entity CSV: {csv_path}")
            
        except Exception as e:
            logger.error(f"Failed to generate entity CSV: {e}")
    
    def _generate_relationship_csv(self, relationships: List[Dict[str, Any]], base_path: Path) -> None:
        """Generate CSV file with relationship data"""
        csv_path = base_path.with_name(f"{base_path.stem}_relationships.csv")
        
        try:
            import csv
            
            with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['source_entity', 'target_entity', 'relationship_type', 
                            'confidence', 'source_document', 'extraction_method']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for rel in relationships:
                    writer.writerow({
                        'source_entity': rel.get('source_entity', ''),
                        'target_entity': rel.get('target_entity', ''),
                        'relationship_type': rel.get('relationship_type', ''),
                        'confidence': rel.get('confidence', 0),
                        'source_document': rel.get('source_document', ''),
                        'extraction_method': rel.get('extraction_method', '')
                    })
            
            logger.info(f"Generated relationship CSV: {csv_path}")
            
        except Exception as e:
            logger.error(f"Failed to generate relationship CSV: {e}")
    
    def get_export_statistics(self) -> Dict[str, Any]:
        """Get export system statistics"""
        return {
            'total_exports': self.export_stats['total_exports'],
            'successful_exports': self.export_stats['successful_exports'],
            'failed_exports': self.export_stats['failed_exports'],
            'success_rate': (self.export_stats['successful_exports'] / 
                           max(1, self.export_stats['total_exports'])) * 100,
            'formats_used': dict(self.export_stats['formats_used']),
            'recent_exports': self.export_stats['export_history'][-10:]  # Last 10 exports
        }
    
    def compile_latex_document(self, tex_path: str, output_dir: Optional[str] = None) -> bool:
        """Compile LaTeX document to PDF"""
        try:
            tex_path = Path(tex_path)
            if not tex_path.exists():
                logger.error(f"LaTeX file not found: {tex_path}")
                return False
            
            if output_dir:
                output_dir = Path(output_dir)
                output_dir.mkdir(parents=True, exist_ok=True)
            else:
                output_dir = tex_path.parent
            
            # Check if pdflatex is available
            if not shutil.which('pdflatex'):
                logger.warning("pdflatex not found - cannot compile LaTeX document")
                return False
            
            # Compile LaTeX document (run twice for references)
            for run in range(2):
                result = subprocess.run([
                    'pdflatex', 
                    '-output-directory', str(output_dir),
                    '-interaction=nonstopmode',
                    str(tex_path)
                ], capture_output=True, text=True)
                
                if result.returncode != 0:
                    logger.error(f"LaTeX compilation failed (run {run + 1}): {result.stderr}")
                    return False
            
            # Run bibtex if bibliography file exists
            bib_path = tex_path.with_suffix('.bib')
            if bib_path.exists() and shutil.which('bibtex'):
                aux_path = output_dir / tex_path.with_suffix('.aux').name
                if aux_path.exists():
                    subprocess.run(['bibtex', str(aux_path)], capture_output=True)
                    
                    # Final pdflatex run after bibtex
                    subprocess.run([
                        'pdflatex', 
                        '-output-directory', str(output_dir),
                        '-interaction=nonstopmode',
                        str(tex_path)
                    ], capture_output=True)
            
            pdf_path = output_dir / tex_path.with_suffix('.pdf').name
            if pdf_path.exists():
                logger.info(f"LaTeX document compiled successfully: {pdf_path}")
                return True
            else:
                logger.error("PDF was not generated")
                return False
                
        except Exception as e:
            logger.error(f"LaTeX compilation error: {e}")
            return False


# Factory functions for common export scenarios
def create_academic_paper_exporter() -> ResearchExporter:
    """Create exporter configured for academic papers"""
    return ResearchExporter()

def create_research_report_exporter() -> ResearchExporter:
    """Create exporter configured for research reports"""
    return ResearchExporter()

# Example usage and testing
if __name__ == "__main__":
    def test_latex_export():
        """Test LaTeX export functionality"""
        
        # Create sample data
        entities = [
            EntityProfile(
                entity_id="ent_001",
                canonical_name="Machine Learning",
                entity_type="CONCEPT",
                aliases=["ML", "Artificial Intelligence"],
                attributes={"domain": "Computer Science", "popularity": "high"},
                confidence_score=0.95,
                source_documents=["doc1.pdf", "doc2.pdf"],
                relationships=[
                    {"relationship_type": "related_to", "target_entity": "Deep Learning", "confidence": 0.9}
                ],
                mentions=[{"surface_form": "ML", "document": "doc1.pdf", "position": 100}]
            ),
            EntityProfile(
                entity_id="ent_002",
                canonical_name="Deep Learning",
                entity_type="CONCEPT",
                aliases=["DL", "Neural Networks"],
                attributes={"domain": "Computer Science", "complexity": "high"},
                confidence_score=0.92,
                source_documents=["doc1.pdf", "doc3.pdf"],
                relationships=[
                    {"relationship_type": "subset_of", "target_entity": "Machine Learning", "confidence": 0.95}
                ],
                mentions=[{"surface_form": "Deep Learning", "document": "doc1.pdf", "position": 200}]
            )
        ]
        
        documents = [
            ResearchDocument(
                document_id="doc1",
                title="Introduction to Machine Learning",
                authors=["John Smith", "Jane Doe"],
                publication_year=2023,
                journal="Journal of AI Research",
                doi="10.1234/jair.2023.001",
                abstract="This paper provides an introduction to machine learning concepts and techniques."
            )
        ]
        
        relationships = [
            {
                "source_entity": "Machine Learning",
                "target_entity": "Deep Learning",
                "relationship_type": "includes",
                "confidence": 0.9,
                "source_document": "doc1.pdf"
            }
        ]
        
        analysis_results = [
            AnalysisResult(
                analysis_id="analysis_001",
                analysis_type="concept_analysis",
                title="Concept Relationship Analysis",
                description="Analysis of conceptual relationships in the document collection",
                results={"total_concepts": 50, "relationship_strength": 0.85},
                confidence_metrics={"precision": 0.9, "recall": 0.8}
            )
        ]
        
        # Create export configuration
        config = ExportConfiguration(
            format=ExportFormat.LATEX_ARTICLE,
            output_path="test_export.tex",
            citation_style=CitationStyle.APA,
            include_bibliography=True,
            include_entity_profiles=True,
            include_relationship_network=True,
            include_analysis_results=True,
            confidence_threshold=0.8,
            custom_metadata={
                "title": "Research Analysis Results",
                "author": "KGAS Research System",
                "abstract": "This report presents comprehensive analysis of research documents using automated entity extraction and relationship discovery.",
                "key_findings": [
                    "Identified 50 key concepts across the document collection",
                    "Discovered 25 significant relationships between entities",
                    "Achieved 90% precision in entity extraction"
                ]
            }
        )
        
        # Create exporter and export
        exporter = create_academic_paper_exporter()
        success = exporter.export_research_results(
            entities, documents, relationships, analysis_results, config
        )
        
        if success:
            print("Export completed successfully!")
            
            # Try to compile LaTeX if possible
            if exporter.compile_latex_document("test_export.tex"):
                print("LaTeX compilation successful!")
            else:
                print("LaTeX compilation skipped or failed")
            
            # Show statistics
            stats = exporter.get_export_statistics()
            print(f"Export Statistics: {stats}")
        else:
            print("Export failed!")
    
    test_latex_export()