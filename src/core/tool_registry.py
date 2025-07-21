"""
Tool Registry for KGAS

This module provides the authoritative registry of all tools, including
current versions, archived versions, and conflict resolutions.

Following fail-fast principles:
- All tools listed here must pass functional validation
- Version conflicts must be explicitly resolved
- Archive decisions must be documented with rationale
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum

class ToolStatus(Enum):
    """Tool status based on validation evidence."""
    FUNCTIONAL = "functional"
    BROKEN = "broken"
    MISSING = "missing"
    NEEDS_VALIDATION = "needs_validation"
    ARCHIVED = "archived"

class ToolRegistry:
    """Central registry for all KGAS tools with version management."""
    
    def __init__(self):
        """Initialize tool registry with current validation data."""
        
        # Based on validation results from 2025-07-19T08:22:37.564654
        self.validation_date = "2025-07-19T08:22:37.564654"
        self.current_tools = self._initialize_current_tools()
        self.archived_tools = self._initialize_archived_tools()
        self.version_conflicts = self._initialize_version_conflicts()
        self.missing_tools = self._initialize_missing_tools()
    
    def _initialize_current_tools(self) -> Dict[str, Dict[str, Any]]:
        """Initialize current tool registry based on validation evidence."""
        
        return {
            "T01": {
                "path": "src/tools/phase1/t01_pdf_loader.py",
                "class": "PDFLoader",
                "status": ToolStatus.FUNCTIONAL,
                "validation_date": self.validation_date,
                "issues": [],
                "description": "PDF document loader with provenance tracking",
                "execute_signature": "(input_data: Any, context: Optional[Dict] = None) -> Dict[str, Any]"
            },
            "T15a": {
                "path": "src/tools/phase1/t15a_text_chunker.py", 
                "class": "TextChunker",
                "status": ToolStatus.FUNCTIONAL,
                "validation_date": self.validation_date,
                "issues": [],
                "description": "Text chunking with configurable size and overlap",
                "execute_signature": "(input_data: Any, context: Optional[Dict] = None) -> Dict[str, Any]"
            },
            "T15b": {
                "path": "src/tools/phase1/t15b_vector_embedder.py",
                "class": "VectorEmbedder", 
                "status": ToolStatus.BROKEN,
                "validation_date": self.validation_date,
                "issues": ["Import error: attempted relative import with no known parent package"],
                "description": "Vector embedding generation with metadata"
            },
            "T23a": {
                "path": "src/tools/phase1/t23a_spacy_ner.py",
                "class": "SpacyNER",
                "status": ToolStatus.FUNCTIONAL,
                "validation_date": self.validation_date,
                "issues": [],
                "description": "SpaCy-based named entity recognition",
                "execute_signature": "(input_data: Any, context: Optional[Dict] = None) -> Dict[str, Any]"
            },
            "T27": {
                "path": "src/tools/phase1/t27_relationship_extractor.py",
                "class": "RelationshipExtractor", 
                "status": ToolStatus.BROKEN,
                "validation_date": self.validation_date,
                "issues": ["Tool requires parameters for execution"],
                "description": "Relationship extraction from text",
                "execute_signature": "(input_data: Any, context: Optional[Dict] = None) -> Dict[str, Any]"
            },
            "T34": {
                "path": "src/tools/phase1/t34_edge_builder.py",
                "class": "EdgeBuilder",
                "status": ToolStatus.BROKEN, 
                "validation_date": self.validation_date,
                "issues": ["Failed to instantiate tool: name 'get_config' is not defined"],
                "description": "Graph edge creation from relationships"
            },
            "T301": {
                "path": "src/tools/phase3/t301_multi_document_fusion.py",
                "class": "MultiDocumentFusion",
                "status": ToolStatus.BROKEN,
                "validation_date": self.validation_date,
                "issues": ["No tool class found in module"],
                "description": "Cross-document entity resolution and fusion"
            },
            "GraphTableExporter": {
                "path": "src/tools/cross_modal/graph_table_exporter.py",
                "class": "GraphTableExporter",
                "status": ToolStatus.FUNCTIONAL,
                "validation_date": self.validation_date,
                "issues": [],
                "description": "Export Neo4j subgraphs to statistical formats",
                "execute_signature": "(input_data: Any, context: Optional[Dict] = None) -> Dict[str, Any]"
            },
            "MultiFormatExporter": {
                "path": "src/tools/cross_modal/multi_format_exporter.py",
                "class": "MultiFormatExporter", 
                "status": ToolStatus.FUNCTIONAL,
                "validation_date": self.validation_date,
                "issues": [],
                "description": "Export results in academic formats (LaTeX, BibTeX)",
                "execute_signature": "(input_data: Any, context: Optional[Dict] = None) -> Dict[str, Any]"
            },
            "T68": {
                "path": "src/tools/phase1/t68_pagerank_optimized.py",
                "class": "T68PageRankOptimized",
                "status": ToolStatus.FUNCTIONAL,
                "validation_date": self.validation_date,
                "issues": [],
                "description": "Optimized PageRank graph analysis",
                "execute_signature": "(input_data: Any = None, context: Optional[Dict] = None) -> Dict[str, Any]"
            }
        }
    
    def _initialize_archived_tools(self) -> Dict[str, Dict[str, Any]]:
        """Initialize archived tools registry."""
        
        # No tools archived yet - will be populated during conflict resolution
        return {}
    
    def _initialize_version_conflicts(self) -> Dict[str, Dict[str, Any]]:
        """Initialize version conflicts that need resolution."""
        
        return {
            "t23c": {
                "description": "LLM-based entity extraction",
                "versions": [
                    {
                        "path": "src/tools/phase1/t23c_llm_entity_extractor.py",
                        "class": "LLMEntityExtractor",
                        "status": ToolStatus.BROKEN,
                        "issues": ["Tool requires parameters: ['input_data', 'context']"],
                        "notes": "Basic LLM entity extraction"
                    },
                    {
                        "path": "src/tools/phase2/t23c_ontology_aware_extractor.py", 
                        "class": "OntologyAwareExtractor",
                        "status": ToolStatus.BROKEN,
                        "issues": ["Tool requires parameters: ['input_data', 'context']"],
                        "notes": "Ontology-aware entity extraction (more advanced)"
                    }
                ],
                "recommended_primary": "src/tools/phase2/t23c_ontology_aware_extractor.py",
                "rationale": "Phase 2 version supports ontology-aware extraction",
                "resolution_status": "pending"
            },
            "t31": {
                "description": "Entity/graph building",
                "versions": [
                    {
                        "path": "src/tools/phase1/t31_entity_builder.py",
                        "class": "EntityBuilder", 
                        "status": ToolStatus.BROKEN,
                        "issues": ["Tool requires parameters: ['input_data', 'context']"],
                        "notes": "Basic entity building"
                    },
                    {
                        "path": "src/tools/phase2/t31_ontology_graph_builder.py",
                        "class": "OntologyGraphBuilder",
                        "status": ToolStatus.BROKEN,
                        "issues": ["Failed to instantiate tool: Neo4j connection failed"],
                        "notes": "Ontology-aware graph building"
                    }
                ],
                "recommended_primary": "src/tools/phase1/t31_entity_builder.py",
                "rationale": "Need functional testing to determine which works better",
                "resolution_status": "pending"
            },
            "t41": {
                "description": "Text embedding generation",
                "versions": [
                    {
                        "path": "src/tools/phase1/t41_async_text_embedder.py",
                        "class": "Unknown",
                        "status": ToolStatus.BROKEN,
                        "issues": ["No tool class found in module"],
                        "notes": "Async text embedding (aligns with AnyIO strategy)"
                    },
                    {
                        "path": "src/tools/phase1/t41_text_embedder.py",
                        "class": "Unknown",
                        "status": ToolStatus.BROKEN, 
                        "issues": ["No tool class found in module"],
                        "notes": "Sync text embedding"
                    }
                ],
                "recommended_primary": "src/tools/phase1/t41_async_text_embedder.py",
                "rationale": "Async version aligns with AnyIO structured concurrency strategy",
                "resolution_status": "pending"
            },
            "t49": {
                "description": "Multi-hop graph queries",
                "versions": [
                    {
                        "path": "src/tools/phase1/t49_enhanced_query.py",
                        "class": "Unknown",
                        "status": ToolStatus.BROKEN,
                        "issues": ["No tool class found in module"],
                        "notes": "Enhanced query capabilities"
                    },
                    {
                        "path": "src/tools/phase1/t49_multihop_query.py", 
                        "class": "MultiHopQuery",
                        "status": ToolStatus.BROKEN,
                        "issues": ["Tool requires parameters: ['input_data', 'context']"],
                        "notes": "Multi-hop query functionality"
                    }
                ],
                "recommended_primary": "src/tools/phase1/t49_multihop_query.py",
                "rationale": "Multi-hop is core functionality for graph analysis",
                "resolution_status": "pending"
            },
            "t68": {
                "description": "PageRank graph analysis",
                "versions": [
                    {
                        "path": "src/tools/phase1/t68_pagerank.py",
                        "class": "PageRankCalculator",
                        "status": ToolStatus.BROKEN,
                        "issues": ["Tool requires parameters: ['input_data', 'context']"],
                        "notes": "Basic PageRank implementation"
                    },
                    {
                        "path": "src/tools/phase1/t68_pagerank_optimized.py",
                        "class": "Unknown", 
                        "status": ToolStatus.BROKEN,
                        "issues": ["No tool class found in module"],
                        "notes": "Optimized PageRank implementation"
                    }
                ],
                "recommended_primary": "src/tools/phase1/t68_pagerank_optimized.py",
                "rationale": "Optimized version should provide better performance",
                "resolution_status": "pending"
            }
        }
    
    def _initialize_missing_tools(self) -> Dict[str, Dict[str, Any]]:
        """Initialize missing tools that need implementation."""
        
        # Based on latest validation, most previously "missing" tools are actually implemented
        # but have functionality issues (parameter requirements, missing classes)
        return {}
    
    def get_functional_tools(self) -> List[str]:
        """Get list of tools that are currently functional."""
        
        functional_tools = []
        for tool_id, tool_info in self.current_tools.items():
            if tool_info["status"] == ToolStatus.FUNCTIONAL:
                functional_tools.append(tool_id)
        
        return functional_tools
    
    def get_broken_tools(self) -> List[str]:
        """Get list of tools that are broken and need fixing."""
        
        broken_tools = []
        for tool_id, tool_info in self.current_tools.items():
            if tool_info["status"] == ToolStatus.BROKEN:
                broken_tools.append(tool_id)
        
        return broken_tools
    
    def get_version_conflicts(self) -> List[str]:
        """Get list of tools with unresolved version conflicts."""
        
        return [conflict_id for conflict_id, conflict_info in self.version_conflicts.items() 
                if conflict_info["resolution_status"] == "pending"]
    
    def get_missing_tools(self) -> List[str]:
        """Get list of missing tools that need implementation."""
        
        return list(self.missing_tools.keys())
    
    def get_mvrt_completion_status(self) -> Dict[str, Any]:
        """Get MVRT completion status based on current tool state."""
        
        required_mvrt_tools = [
            "T01", "T15a", "T15b", "T23a", "T23c", "T27", "T31", "T34", 
            "T49", "T301", "GraphTableExporter", "MultiFormatExporter"
        ]
        
        functional_count = 0
        total_count = len(required_mvrt_tools)
        
        # Count functional tools
        for tool_id in required_mvrt_tools:
            if tool_id in self.current_tools:
                if self.current_tools[tool_id]["status"] == ToolStatus.FUNCTIONAL:
                    functional_count += 1
            elif tool_id in self.missing_tools:
                # Missing tools are not functional
                pass
        
        completion_percentage = (functional_count / total_count) * 100 if total_count > 0 else 0
        
        return {
            "total_required": total_count,
            "functional": functional_count,
            "completion_percentage": completion_percentage,
            "missing_tools": len(self.missing_tools),
            "version_conflicts": len(self.get_version_conflicts()),
            "broken_tools": len(self.get_broken_tools())
        }
    
    def resolve_version_conflict(self, conflict_id: str, chosen_version_path: str, archive_reason: str) -> None:
        """Resolve a version conflict by choosing primary version and archiving others."""
        
        if conflict_id not in self.version_conflicts:
            raise ValueError(f"No version conflict found for {conflict_id}")
        
        conflict = self.version_conflicts[conflict_id]
        chosen_version = None
        archive_versions = []
        
        # Find chosen version and identify others for archiving
        for version in conflict["versions"]:
            if version["path"] == chosen_version_path:
                chosen_version = version
            else:
                archive_versions.append(version)
        
        if chosen_version is None:
            raise ValueError(f"Chosen version path {chosen_version_path} not found in conflict {conflict_id}")
        
        # Update current tools registry with chosen version
        tool_id = conflict_id.upper()
        self.current_tools[tool_id] = {
            "path": chosen_version["path"],
            "class": chosen_version["class"],
            "status": chosen_version["status"],
            "validation_date": self.validation_date,
            "issues": chosen_version.get("issues", []),
            "description": conflict["description"],
            "resolution_date": datetime.now().isoformat(),
            "resolution_reason": archive_reason
        }
        
        # Archive other versions
        for version in archive_versions:
            archive_key = f"{conflict_id}_{version['path'].split('/')[-1]}"
            self.archived_tools[archive_key] = {
                "original_path": version["path"],
                "archived_path": f"archived/tools/{version['path']}",
                "class": version["class"], 
                "archive_date": datetime.now().isoformat(),
                "archive_reason": archive_reason,
                "replaced_by": chosen_version["path"]
            }
        
        # Mark conflict as resolved
        self.version_conflicts[conflict_id]["resolution_status"] = "resolved"
        self.version_conflicts[conflict_id]["chosen_version"] = chosen_version_path
        self.version_conflicts[conflict_id]["resolution_date"] = datetime.now().isoformat()
    
    def add_tool(self, tool_id: str, tool_info: Dict[str, Any]) -> None:
        """Add a new functional tool to the registry."""
        
        # Validate required fields
        required_fields = ["path", "class", "status", "description"]
        for field in required_fields:
            if field not in tool_info:
                raise ValueError(f"Tool info missing required field: {field}")
        
        # Add validation date
        tool_info["validation_date"] = datetime.now().isoformat()
        
        self.current_tools[tool_id] = tool_info
    
    def mark_tool_functional(self, tool_id: str, validation_evidence: Dict[str, Any]) -> None:
        """Mark a tool as functional with validation evidence."""
        
        if tool_id not in self.current_tools:
            raise ValueError(f"Tool {tool_id} not found in registry")
        
        self.current_tools[tool_id]["status"] = ToolStatus.FUNCTIONAL
        self.current_tools[tool_id]["validation_date"] = datetime.now().isoformat()
        self.current_tools[tool_id]["validation_evidence"] = validation_evidence
        
        # Clear any previous issues
        if "issues" in self.current_tools[tool_id]:
            self.current_tools[tool_id]["issues"] = []
    
    def get_registry_summary(self) -> Dict[str, Any]:
        """Get comprehensive summary of tool registry state."""
        
        mvrt_status = self.get_mvrt_completion_status()
        
        return {
            "registry_metadata": {
                "last_validation": self.validation_date,
                "total_current_tools": len(self.current_tools),
                "total_archived_tools": len(self.archived_tools),
                "total_version_conflicts": len(self.version_conflicts),
                "total_missing_tools": len(self.missing_tools)
            },
            "mvrt_status": mvrt_status,
            "functional_tools": self.get_functional_tools(),
            "broken_tools": self.get_broken_tools(),
            "version_conflicts": self.get_version_conflicts(),
            "missing_tools": self.get_missing_tools(),
            "current_tools": self.current_tools,
            "archived_tools": self.archived_tools,
            "version_conflicts_detail": self.version_conflicts,
            "missing_tools_detail": self.missing_tools
        }

# Global registry instance
tool_registry = ToolRegistry()

def get_tool_registry() -> ToolRegistry:
    """Get the global tool registry instance."""
    return tool_registry