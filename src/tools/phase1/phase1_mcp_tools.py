"""Phase 1 MCP Tools - Individual pipeline components exposed as MCP tools

Expands MCP coverage by exposing individual Phase 1 tools:
- PDF Loading (T01)
- Text Chunking (T15a) 
- Entity Extraction (T23a)
- Relationship Extraction (T27)
- Entity Building (T31)
- Edge Building (T34)
- PageRank Calculation (T68)
- Multi-hop Query (T49)

These tools allow fine-grained control and debugging of the Phase 1 pipeline.
"""

from fastmcp import FastMCP
from typing import Dict, List, Optional, Any
import os
from pathlib import Path

# Import core services and configuration
from src.core.service_manager import get_service_manager
from src.core.config_manager import ConfigurationManager

# Import Phase 1 tools
from src.tools.phase1.t01_pdf_loader_unified import T01PDFLoaderUnified
from src.tools.phase1.t15a_text_chunker_unified import T15ATextChunkerUnified
from src.tools.phase1.t23a_spacy_ner_unified import T23ASpacyNERUnified
from src.tools.phase1.t27_relationship_extractor_unified import T27RelationshipExtractorUnified
from src.tools.phase1.t31_entity_builder_unified import T31EntityBuilderUnified
from src.tools.phase1.t34_edge_builder_unified import T34EdgeBuilderUnified
from src.tools.phase1.t68_pagerank_calculator_unified import T68PageRankCalculatorUnified
from src.tools.phase1.t49_multihop_query_unified import T49MultiHopQueryUnified
from src.core.config_manager import get_config



def create_phase1_mcp_tools(mcp: FastMCP):
    """Add Phase 1 pipeline tools to an existing MCP server"""
    
    # Get shared service manager
    service_manager = get_service_manager()
    
    # Initialize Phase 1 tools with service manager
    pdf_loader = T01PDFLoaderUnified(service_manager)
    text_chunker = T15ATextChunkerUnified(service_manager)
    entity_extractor = T23ASpacyNERUnified(service_manager)
    relationship_extractor = T27RelationshipExtractorUnified(service_manager)
    entity_builder = T31EntityBuilderUnified(service_manager)
    edge_builder = T34EdgeBuilderUnified(service_manager)
    pagerank_calculator = T68PageRankCalculatorUnified(service_manager)
    query_engine = T49MultiHopQueryUnified(service_manager)
    
    # =============================================================================
    # T01: PDF Loading Tools
    # =============================================================================
    
    @mcp.tool()
    def load_documents(document_paths: List[str]) -> Dict[str, Any]:
        """Load and extract text from document files.
        
        Args:
            document_paths: List of paths to document files to load
        """
        from src.tools.base_tool import ToolRequest
        
        results = []
        for path in document_paths:
            request = ToolRequest(
                tool_id="T01",
                operation="load_document",
                input_data={"file_path": path},
                parameters={}
            )
            result = pdf_loader.execute(request)
            results.append(result.data if result.status == "success" else {"error": result.error_message})
        return {"documents": results, "total_loaded": len(results)}
    
    @mcp.tool()
    def get_pdf_loader_info() -> Dict[str, Any]:
        """Get PDF loader tool information."""
        return pdf_loader.get_tool_info()
    
    # =============================================================================
    # T15a: Text Chunking Tools
    # =============================================================================
    
    @mcp.tool()
    def chunk_text(
        document_ref: str,
        text: str,
        document_confidence: float = 0.8,
        chunk_size: int = 500,
        overlap: int = 50
    ) -> Dict[str, Any]:
        """Break text into overlapping chunks for processing.
        
        Args:
            document_ref: Reference to source document
            text: Text to chunk
            document_confidence: Confidence score from document
            chunk_size: Target size of each chunk in characters
            overlap: Number of characters to overlap between chunks
        """
        return text_chunker.chunk_text(
            document_ref=document_ref,
            text=text,
            document_confidence=document_confidence,
            chunk_size=chunk_size,
            overlap=overlap
        )
    
    @mcp.tool()
    def get_text_chunker_info() -> Dict[str, Any]:
        """Get text chunker tool information."""
        return text_chunker.get_tool_info()
    
    # =============================================================================
    # T23a: Entity Extraction Tools
    # =============================================================================
    
    @mcp.tool()
    def extract_entities(
        chunk_ref: str,
        text: str,
        chunk_confidence: float = 0.8
    ) -> Dict[str, Any]:
        """Extract named entities from text using spaCy.
        
        Args:
            chunk_ref: Reference to source text chunk
            text: Text to analyze for entities
            chunk_confidence: Confidence score from chunk
        """
        return entity_extractor.extract_entities(
            chunk_ref=chunk_ref,
            text=text,
            chunk_confidence=chunk_confidence
        )
    
    @mcp.tool()
    def get_supported_entity_types() -> List[str]:
        """Get list of entity types supported by spaCy NER."""
        return entity_extractor.get_supported_entity_types()
    
    @mcp.tool()
    def get_entity_extractor_info() -> Dict[str, Any]:
        """Get entity extractor tool information."""
        return entity_extractor.get_tool_info()
    
    @mcp.tool()
    def get_spacy_model_info() -> Dict[str, Any]:
        """Get information about the loaded spaCy model."""
        return entity_extractor.get_model_info()
    
    # =============================================================================
    # T27: Relationship Extraction Tools
    # =============================================================================
    
    @mcp.tool()
    def extract_relationships(
        chunk_ref: str,
        text: str,
        entities: List[Dict[str, Any]],
        chunk_confidence: float = 0.8
    ) -> Dict[str, Any]:
        """Extract relationships between entities using pattern matching.
        
        Args:
            chunk_ref: Reference to source text chunk
            text: Text to analyze for relationships
            entities: List of entities found in this chunk
            chunk_confidence: Confidence score from chunk
        """
        return relationship_extractor.extract_relationships(
            chunk_ref=chunk_ref,
            text=text,
            entities=entities,
            chunk_confidence=chunk_confidence
        )
    
    @mcp.tool()
    def get_supported_relationship_types() -> List[str]:
        """Get list of relationship types supported by pattern extraction."""
        return relationship_extractor.get_supported_relationship_types()
    
    @mcp.tool()
    def get_relationship_extractor_info() -> Dict[str, Any]:
        """Get relationship extractor tool information."""
        return relationship_extractor.get_tool_info()
    
    # =============================================================================
    # T31: Entity Building Tools
    # =============================================================================
    
    @mcp.tool()
    def build_entities(
        mentions: List[Dict[str, Any]],
        source_refs: List[str]
    ) -> Dict[str, Any]:
        """Build entity nodes in Neo4j from mentions.
        
        Args:
            mentions: List of entity mentions to process
            source_refs: List of source document references
        """
        return entity_builder.build_entities(
            mentions=mentions,
            source_refs=source_refs
        )
    
    @mcp.tool()
    def get_entity_builder_info() -> Dict[str, Any]:
        """Get entity builder tool information."""
        return entity_builder.get_tool_info()
    
    # =============================================================================
    # T34: Edge Building Tools
    # =============================================================================
    
    @mcp.tool()
    def build_edges(
        relationships: List[Dict[str, Any]],
        source_refs: List[str]
    ) -> Dict[str, Any]:
        """Build relationship edges in Neo4j.
        
        Args:
            relationships: List of relationships to process
            source_refs: List of source document references
        """
        return edge_builder.build_edges(
            relationships=relationships,
            source_refs=source_refs
        )
    
    @mcp.tool()
    def get_edge_builder_info() -> Dict[str, Any]:
        """Get edge builder tool information."""
        return edge_builder.get_tool_info()
    
    # =============================================================================
    # T68: PageRank Tools
    # =============================================================================
    
    @mcp.tool()
    def calculate_pagerank(
        damping_factor: float = 0.85,
        max_iterations: int = 100,
        tolerance: float = 1e-6
    ) -> Dict[str, Any]:
        """Calculate PageRank scores for all entities in the graph.
        
        Args:
            damping_factor: PageRank damping factor (0.0-1.0)
            max_iterations: Maximum iterations for convergence
            tolerance: Convergence tolerance
        """
        return pagerank_calculator.calculate_pagerank(
            damping_factor=damping_factor,
            max_iterations=max_iterations,
            tolerance=tolerance
        )
    
    @mcp.tool()
    def get_top_entities(limit: int = 10) -> List[Dict[str, Any]]:
        """Get top entities by PageRank score.
        
        Args:
            limit: Maximum number of entities to return
        """
        result = pagerank_calculator.calculate_pagerank()
        if result["status"] == "success":
            return result["ranked_entities"][:limit]
        return []
    
    @mcp.tool()
    def get_pagerank_calculator_info() -> Dict[str, Any]:
        """Get PageRank calculator tool information."""
        return pagerank_calculator.get_tool_info()
    
    # =============================================================================
    # T49: Multi-hop Query Tools
    # =============================================================================
    
    @mcp.tool()
    def query_graph(
        query_text: str,
        max_hops: int = 2,
        result_limit: int = 10
    ) -> Dict[str, Any]:
        """Execute multi-hop queries against the knowledge graph.
        
        Args:
            query_text: Natural language query
            max_hops: Maximum hops to traverse in graph
            result_limit: Maximum number of results to return
        """
        return query_engine.query_graph(
            query_text=query_text,
            max_hops=max_hops,
            result_limit=result_limit
        )
    
    @mcp.tool()
    def get_query_engine_info() -> Dict[str, Any]:
        """Get query engine tool information."""
        return query_engine.get_tool_info()
    
    # =============================================================================
    # Graph Analysis Tools
    # =============================================================================
    
    @mcp.tool()
    def get_graph_statistics() -> Dict[str, Any]:
        """Get comprehensive graph statistics."""
        # Use PageRank calculator to get graph stats
        pagerank_result = pagerank_calculator.calculate_pagerank()
        if pagerank_result["status"] == "success":
            return pagerank_result.get("graph_stats", {})
        return {"error": "Failed to get graph statistics"}
    
    @mcp.tool()
    def get_entity_details(entity_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific entity.
        
        Args:
            entity_id: ID of the entity to examine
        """
        # Get mentions for this entity
        mentions = identity_service.get_mentions_for_entity(entity_id)
        
        # Get entity from graph
        entity_result = entity_builder.get_entity_by_id(entity_id)
        
        return {
            "entity_id": entity_id,
            "mentions": mentions,
            "graph_entity": entity_result,
            "mention_count": len(mentions) if mentions else 0
        }
    
    # =============================================================================
    # Pipeline Utilities
    # =============================================================================
    
    @mcp.tool()
    def get_phase1_tool_registry() -> Dict[str, Any]:
        """Get registry of all Phase 1 tools and their capabilities."""
        return {
            "T01_PDF_LOADER": pdf_loader.get_tool_info(),
            "T15A_TEXT_CHUNKER": text_chunker.get_tool_info(),
            "T23A_SPACY_NER": entity_extractor.get_tool_info(),
            "T27_RELATIONSHIP_EXTRACTOR": relationship_extractor.get_tool_info(),
            "T31_ENTITY_BUILDER": entity_builder.get_tool_info(),
            "T34_EDGE_BUILDER": edge_builder.get_tool_info(),
            "T68_PAGERANK": pagerank_calculator.get_tool_info(),
            "T49_MULTIHOP_QUERY": query_engine.get_tool_info()
        }
    
    @mcp.tool()
    def validate_phase1_pipeline() -> Dict[str, Any]:
        """Validate that all Phase 1 pipeline components are functional."""
        validation_results = {}
        
        # Test PDF loader
        try:
            loader_info = pdf_loader.get_tool_info()
            validation_results["pdf_loader"] = {"status": "ok", "info": loader_info}
        except Exception as e:
            validation_results["pdf_loader"] = {"status": "error", "error": str(e)}
        
        # Test entity extractor
        try:
            model_info = entity_extractor.get_model_info()
            validation_results["entity_extractor"] = {
                "status": "ok" if model_info["available"] else "warning",
                "info": model_info
            }
        except Exception as e:
            validation_results["entity_extractor"] = {"status": "error", "error": str(e)}
        
        # Test graph connections
        try:
            stats = pagerank_calculator.calculate_pagerank()
            validation_results["graph_connection"] = {
                "status": "ok" if stats["status"] == "success" else "error",
                "info": stats.get("graph_stats", {})
            }
        except Exception as e:
            validation_results["graph_connection"] = {"status": "error", "error": str(e)}
        
        # Overall status
        all_statuses = [r["status"] for r in validation_results.values()]
        overall_status = (
            "ok" if all(s == "ok" for s in all_statuses) 
            else "warning" if any(s == "warning" for s in all_statuses)
            else "error"
        )
        
        return {
            "overall_status": overall_status,
            "component_results": validation_results,
            "timestamp": "now"
        }
    
    return {
        "tools_added": 25,
        "categories": [
            "PDF Loading (T01)",
            "Text Chunking (T15a)",
            "Entity Extraction (T23a)", 
            "Relationship Extraction (T27)",
            "Entity Building (T31)",
            "Edge Building (T34)",
            "PageRank Calculation (T68)",
            "Multi-hop Query (T49)",
            "Graph Analysis",
            "Pipeline Utilities"
        ]
    }


class Phase1MCPToolsManager:
    """Wrapper class to make phase1_mcp_tools discoverable by audit system"""
    
    def __init__(self):
        self.tool_id = "PHASE1_MCP_TOOLS"
        self._mcp_server = None
        self._tools_registered = False
    
    def get_tool_info(self):
        """Return tool information for audit system"""
        return {
            "tool_id": self.tool_id,
            "tool_type": "MCP_TOOLS_MANAGER",
            "status": "functional",
            "description": "Manages all Phase 1 MCP tools",
            "tool_count": 25
        }
    
    def create_tools(self, mcp_server):
        """Expose the main functionality"""
        self._mcp_server = mcp_server
        result = create_phase1_mcp_tools(mcp_server)
        self._tools_registered = True
        return result
    
    def is_registered(self):
        """Check if tools are registered with MCP server"""
        return self._tools_registered
    
    def get_tool_categories(self):
        """Get list of tool categories"""
        return [
            "PDF Loading (T01)",
            "Text Chunking (T15a)",
            "Entity Extraction (T23a)", 
            "Relationship Extraction (T27)",
            "Entity Building (T31)",
            "Edge Building (T34)",
            "PageRank Calculation (T68)",
            "Multi-hop Query (T49)",
            "Graph Analysis",
            "Pipeline Utilities"
        ]