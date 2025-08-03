"""
Pipeline MCP Tools

Additional tools for pipeline orchestration and Phase 1 processing.
"""

import logging
from typing import Dict, Any, List, Optional
from fastmcp import FastMCP

from .server_config import get_mcp_config

logger = logging.getLogger(__name__)


class PipelineTools:
    """Collection of Pipeline tools for MCP server"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config = get_mcp_config()
    
    @property
    def orchestrator(self):
        """Get pipeline orchestrator instance"""
        return self.config.orchestrator
    
    def register_tools(self, mcp: FastMCP):
        """Register all pipeline tools with MCP server"""
        
        @mcp.tool()
        def load_pdf_document(
            file_path: str,
            document_ref: str = None
        ) -> Dict[str, Any]:
            """Load and process a PDF document.
            
            Args:
                file_path: Path to the PDF file
                document_ref: Optional document reference
            """
            try:
                # Import Phase 1 tools for actual processing
                from src.tools.phase1.phase1_mcp_tools import create_phase1_mcp_tools
                phase1_tools = create_phase1_mcp_tools()
                
                return phase1_tools.load_pdf_document(file_path, document_ref)
            except Exception as e:
                self.logger.error(f"Error loading PDF document: {e}")
                return {"error": str(e)}
        
        @mcp.tool()
        def chunk_text(
            text: str,
            document_ref: str = "test_doc",
            chunk_size: int = 1000,
            overlap: int = 200
        ) -> Dict[str, Any]:
            """Chunk text into smaller pieces.
            
            Args:
                text: Text to chunk
                document_ref: Document reference
                chunk_size: Size of each chunk
                overlap: Overlap between chunks
            """
            try:
                from src.tools.phase1.phase1_mcp_tools import create_phase1_mcp_tools
                phase1_tools = create_phase1_mcp_tools()
                
                return phase1_tools.chunk_text(text, document_ref, chunk_size, overlap)
            except Exception as e:
                self.logger.error(f"Error chunking text: {e}")
                return {"error": str(e)}
        
        @mcp.tool()
        def extract_entities_from_text(
            text: str,
            chunk_ref: str = "test_chunk"
        ) -> Dict[str, Any]:
            """Extract named entities from text.
            
            Args:
                text: Text to extract entities from
                chunk_ref: Chunk reference
            """
            try:
                from src.tools.phase1.phase1_mcp_tools import create_phase1_mcp_tools
                phase1_tools = create_phase1_mcp_tools()
                
                return phase1_tools.extract_entities_from_text(text, chunk_ref)
            except Exception as e:
                self.logger.error(f"Error extracting entities: {e}")
                return {"error": str(e)}
        
        @mcp.tool()
        def extract_relationships(
            text: str,
            entities: List[Dict[str, Any]],
            chunk_ref: str = "test_chunk"
        ) -> Dict[str, Any]:
            """Extract relationships between entities.
            
            Args:
                text: Source text
                entities: List of entities to find relationships between
                chunk_ref: Chunk reference
            """
            try:
                from src.tools.phase1.phase1_mcp_tools import create_phase1_mcp_tools
                phase1_tools = create_phase1_mcp_tools()
                
                return phase1_tools.extract_relationships(text, entities, chunk_ref)
            except Exception as e:
                self.logger.error(f"Error extracting relationships: {e}")
                return {"error": str(e)}
        
        @mcp.tool()
        def build_graph_entities(
            entities: List[Dict[str, Any]],
            chunk_ref: str = "test_chunk"
        ) -> Dict[str, Any]:
            """Build graph entities from extracted entities.
            
            Args:
                entities: List of entities
                chunk_ref: Chunk reference
            """
            try:
                from src.tools.phase1.phase1_mcp_tools import create_phase1_mcp_tools
                phase1_tools = create_phase1_mcp_tools()
                
                return phase1_tools.build_graph_entities(entities, chunk_ref)
            except Exception as e:
                self.logger.error(f"Error building graph entities: {e}")
                return {"error": str(e)}
        
        @mcp.tool()
        def build_graph_edges(
            relationships: List[Dict[str, Any]],
            chunk_ref: str = "test_chunk"
        ) -> Dict[str, Any]:
            """Build graph edges from extracted relationships.
            
            Args:
                relationships: List of relationships
                chunk_ref: Chunk reference
            """
            try:
                from src.tools.phase1.phase1_mcp_tools import create_phase1_mcp_tools
                phase1_tools = create_phase1_mcp_tools()
                
                return phase1_tools.build_graph_edges(relationships, chunk_ref)
            except Exception as e:
                self.logger.error(f"Error building graph edges: {e}")
                return {"error": str(e)}
        
        @mcp.tool()
        def calculate_pagerank(
            damping_factor: float = 0.85,
            max_iterations: int = 100,
            tolerance: float = 1e-6
        ) -> Dict[str, Any]:
            """Calculate PageRank scores for the graph.
            
            Args:
                damping_factor: PageRank damping factor
                max_iterations: Maximum iterations
                tolerance: Convergence tolerance
            """
            try:
                from src.tools.phase1.phase1_mcp_tools import create_phase1_mcp_tools
                phase1_tools = create_phase1_mcp_tools()
                
                return phase1_tools.calculate_pagerank(damping_factor, max_iterations, tolerance)
            except Exception as e:
                self.logger.error(f"Error calculating PageRank: {e}")
                return {"error": str(e)}
        
        @mcp.tool()
        def query_graph(
            query_text: str,
            max_results: int = 10,
            include_relationships: bool = True
        ) -> Dict[str, Any]:
            """Query the knowledge graph.
            
            Args:
                query_text: Natural language query
                max_results: Maximum number of results
                include_relationships: Whether to include relationships
            """
            try:
                from src.tools.phase1.phase1_mcp_tools import create_phase1_mcp_tools
                phase1_tools = create_phase1_mcp_tools()
                
                return phase1_tools.query_graph(query_text, max_results, include_relationships)
            except Exception as e:
                self.logger.error(f"Error querying graph: {e}")
                return {"error": str(e)}
        
        @mcp.tool()
        def process_document_complete_pipeline(
            file_path: str,
            include_pagerank: bool = True
        ) -> Dict[str, Any]:
            """Process a document through the complete pipeline.
            
            Args:
                file_path: Path to the document file
                include_pagerank: Whether to calculate PageRank
            """
            try:
                from src.tools.phase1.phase1_mcp_tools import create_phase1_mcp_tools
                phase1_tools = create_phase1_mcp_tools()
                
                return phase1_tools.process_document_complete_pipeline(file_path, include_pagerank)
            except Exception as e:
                self.logger.error(f"Error processing document pipeline: {e}")
                return {"error": str(e)}
        
        @mcp.tool()
        def get_kgas_system_status() -> Dict[str, Any]:
            """Get comprehensive KGAS system status."""
            try:
                from src.tools.phase1.phase1_mcp_tools import create_phase1_mcp_tools
                phase1_tools = create_phase1_mcp_tools()
                
                return phase1_tools.get_kgas_system_status()
            except Exception as e:
                self.logger.error(f"Error getting KGAS system status: {e}")
                return {"error": str(e)}
        
        @mcp.tool()
        def execute_pdf_to_answer_workflow(
            pdf_path: str,
            question: str
        ) -> Dict[str, Any]:
            """Execute complete PDF to answer workflow.
            
            Args:
                pdf_path: Path to PDF file
                question: Question to answer
            """
            try:
                if not self.orchestrator:
                    return {"error": "Orchestrator not available"}
                
                # Use orchestrator for complete workflow
                return self.orchestrator.execute_pdf_to_answer_workflow(pdf_path, question)
            except Exception as e:
                self.logger.error(f"Error executing PDF to answer workflow: {e}")
                return {"error": str(e)}
        
        @mcp.tool()
        def get_orchestrator_info() -> Dict[str, Any]:
            """Get pipeline orchestrator information."""
            try:
                if not self.orchestrator:
                    return {"error": "Orchestrator not available", "available": False}
                
                return {
                    "available": True,
                    "info": self.orchestrator.get_tool_info() if hasattr(self.orchestrator, 'get_tool_info') else "No info available"
                }
            except Exception as e:
                self.logger.error(f"Error getting orchestrator info: {e}")
                return {"error": str(e)}
        
        self.logger.info("Pipeline tools registered successfully")
    
    def get_tool_info(self) -> Dict[str, Any]:
        """Get information about pipeline tools"""
        return {
            "service": "Pipeline_Tools",
            "tool_count": 12,
            "tools": [
                "load_pdf_document",
                "chunk_text",
                "extract_entities_from_text",
                "extract_relationships",
                "build_graph_entities",
                "build_graph_edges",
                "calculate_pagerank",
                "query_graph",
                "process_document_complete_pipeline",
                "get_kgas_system_status",
                "execute_pdf_to_answer_workflow",
                "get_orchestrator_info"
            ],
            "description": "Pipeline orchestration and Phase 1 processing tools",
            "capabilities": [
                "document_processing",
                "entity_extraction",
                "relationship_extraction",
                "graph_building",
                "pagerank_calculation",
                "graph_querying",
                "workflow_orchestration"
            ],
            "orchestrator_available": self.orchestrator is not None
        }