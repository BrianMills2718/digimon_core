#!/usr/bin/env python3
"""
KGAS Simple MCP Server - Fast implementation for testing

Exposes the core KGAS tools with a simple interface for immediate testing.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from fastmcp import FastMCP
except ImportError:
    print("FastMCP not found. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "fastmcp"])
    from fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server
mcp = FastMCP("KGAS Simple Tools")


def get_service_manager():
    """Get service manager if available"""
    try:
        from src.core.service_manager import get_service_manager
        return get_service_manager()
    except Exception as e:
        logger.error(f"Failed to get service manager: {e}")
        return None


@mcp.tool()
def test_kgas_tools() -> Dict[str, Any]:
    """Test which KGAS tools are available and working."""
    results = {}
    
    # Test service manager
    try:
        service_manager = get_service_manager()
        results["service_manager"] = "available" if service_manager else "unavailable"
    except Exception as e:
        results["service_manager"] = f"error: {str(e)}"
    
    # Test individual tools
    tools_to_test = [
        ("T01_PDF_Loader", "src.tools.phase1.t01_pdf_loader_unified", "T01PDFLoaderUnified"),
        ("T15A_Text_Chunker", "src.tools.phase1.t15a_text_chunker_unified", "T15ATextChunkerUnified"),
        ("T23A_SpaCy_NER", "src.tools.phase1.t23a_spacy_ner_unified", "T23ASpacyNERUnified"),
        ("T27_Relationship_Extractor", "src.tools.phase1.t27_relationship_extractor_unified", "T27RelationshipExtractorUnified"),
        ("T31_Entity_Builder", "src.tools.phase1.t31_entity_builder_unified", "T31EntityBuilderUnified"),
        ("T34_Edge_Builder", "src.tools.phase1.t34_edge_builder_unified", "T34EdgeBuilderUnified"),
        ("T68_PageRank", "src.tools.phase1.t68_pagerank_calculator_unified", "T68PageRankCalculatorUnified"),
        ("T49_MultiHop_Query", "src.tools.phase1.t49_multihop_query_unified", "T49MultiHopQueryUnified")
    ]
    
    for tool_name, module_path, class_name in tools_to_test:
        try:
            module = __import__(module_path, fromlist=[class_name])
            tool_class = getattr(module, class_name)
            
            # Test if we can instantiate it
            if get_service_manager():
                tool = tool_class(get_service_manager())
                contract = tool.get_contract()
                results[tool_name] = {
                    "status": "available",
                    "tool_id": contract.tool_id,
                    "name": contract.name,
                    "description": contract.description
                }
            else:
                results[tool_name] = "service_manager_required"
                
        except Exception as e:
            results[tool_name] = f"error: {str(e)}"
    
    return results


@mcp.tool()
def load_pdf_document(file_path: str) -> Dict[str, Any]:
    """Load and process a PDF document using T01."""
    try:
        from src.tools.phase1.t01_pdf_loader_unified import T01PDFLoaderUnified
        from src.tools.base_tool import ToolRequest
        
        service_manager = get_service_manager()
        if not service_manager:
            return {"error": "Service manager not available"}
        
        loader = T01PDFLoaderUnified(service_manager)
        
        request = ToolRequest(
            tool_id="T01",
            operation="load_document",
            input_data={"file_path": file_path},
            parameters={}
        )
        
        result = loader.execute(request)
        
        if result.status == "success":
            return {
                "status": "success",
                "document": result.data,
                "execution_time": result.execution_time,
                "memory_used": result.memory_used
            }
        else:
            return {
                "status": "error",
                "error_code": result.error_code,
                "error_message": result.error_message
            }
            
    except Exception as e:
        return {"error": f"Failed to load document: {str(e)}"}


@mcp.tool()
def extract_entities_from_text(text: str, chunk_ref: str = "test_chunk") -> Dict[str, Any]:
    """Extract named entities from text using T23A."""
    try:
        from src.tools.phase1.t23a_spacy_ner_unified import T23ASpacyNERUnified
        from src.tools.base_tool import ToolRequest
        
        service_manager = get_service_manager()
        if not service_manager:
            return {"error": "Service manager not available"}
        
        ner = T23ASpacyNERUnified(service_manager)
        
        request = ToolRequest(
            tool_id="T23A",
            operation="extract_entities",
            input_data={
                "text": text,
                "chunk_ref": chunk_ref
            },
            parameters={}
        )
        
        result = ner.execute(request)
        
        if result.status == "success":
            return {
                "status": "success",
                "entities": result.data,
                "execution_time": result.execution_time
            }
        else:
            return {
                "status": "error",
                "error_code": result.error_code,
                "error_message": result.error_message
            }
            
    except Exception as e:
        return {"error": f"Failed to extract entities: {str(e)}"}


@mcp.tool()
def chunk_text(text: str, document_ref: str = "test_doc") -> Dict[str, Any]:
    """Chunk text into smaller pieces using T15A."""
    try:
        from src.tools.phase1.t15a_text_chunker_unified import T15ATextChunkerUnified
        from src.tools.base_tool import ToolRequest
        
        service_manager = get_service_manager()
        if not service_manager:
            return {"error": "Service manager not available"}
        
        chunker = T15ATextChunkerUnified(service_manager)
        
        request = ToolRequest(
            tool_id="T15A",
            operation="chunk_text",
            input_data={
                "text": text,
                "document_ref": document_ref
            },
            parameters={}
        )
        
        result = chunker.execute(request)
        
        if result.status == "success":
            return {
                "status": "success",
                "chunks": result.data,
                "execution_time": result.execution_time
            }
        else:
            return {
                "status": "error",
                "error_code": result.error_code,
                "error_message": result.error_message
            }
            
    except Exception as e:
        return {"error": f"Failed to chunk text: {str(e)}"}


@mcp.tool()
def calculate_pagerank() -> Dict[str, Any]:
    """Calculate PageRank scores using T68."""
    try:
        from src.tools.phase1.t68_pagerank_calculator_unified import T68PageRankCalculatorUnified
        from src.tools.base_tool import ToolRequest
        
        service_manager = get_service_manager()
        if not service_manager:
            return {"error": "Service manager not available"}
        
        pagerank = T68PageRankCalculatorUnified(service_manager)
        
        request = ToolRequest(
            tool_id="T68",
            operation="calculate_pagerank",
            input_data={},
            parameters={}
        )
        
        result = pagerank.execute(request)
        
        if result.status == "success":
            return {
                "status": "success",
                "pagerank_results": result.data,
                "execution_time": result.execution_time
            }
        else:
            return {
                "status": "error",
                "error_code": result.error_code,
                "error_message": result.error_message
            }
            
    except Exception as e:
        return {"error": f"Failed to calculate PageRank: {str(e)}"}


@mcp.tool()
def query_graph(query_text: str) -> Dict[str, Any]:
    """Query the knowledge graph using T49."""
    try:
        from src.tools.phase1.t49_multihop_query_unified import T49MultiHopQueryUnified
        from src.tools.base_tool import ToolRequest
        
        service_manager = get_service_manager()
        if not service_manager:
            return {"error": "Service manager not available"}
        
        query_engine = T49MultiHopQueryUnified(service_manager)
        
        request = ToolRequest(
            tool_id="T49",
            operation="query_graph",
            input_data={"query_text": query_text},
            parameters={}
        )
        
        result = query_engine.execute(request)
        
        if result.status == "success":
            return {
                "status": "success",
                "query_results": result.data,
                "execution_time": result.execution_time
            }
        else:
            return {
                "status": "error",
                "error_code": result.error_code,
                "error_message": result.error_message
            }
            
    except Exception as e:
        return {"error": f"Failed to query graph: {str(e)}"}


@mcp.tool()
def get_kgas_system_status() -> Dict[str, Any]:
    """Get overall KGAS system status."""
    try:
        # Check core services
        service_manager = get_service_manager()
        services_status = "available" if service_manager else "unavailable"
        
        # Check Neo4j if possible
        neo4j_status = "unknown"
        try:
            from src.core.neo4j_manager import Neo4jManager
            neo4j_manager = Neo4jManager()
            neo4j_status = "connected" if hasattr(neo4j_manager, 'driver') and neo4j_manager.driver else "disconnected"
        except Exception:
            neo4j_status = "unavailable"
        
        return {
            "system_status": "operational" if services_status == "available" else "degraded",
            "core_services": services_status,
            "neo4j_connection": neo4j_status,
            "working_directory": str(project_root),
            "available_tools": [
                "load_pdf_document",
                "chunk_text", 
                "extract_entities_from_text",
                "calculate_pagerank",
                "query_graph"
            ]
        }
        
    except Exception as e:
        return {
            "system_status": "error",
            "error": str(e)
        }


def main():
    """Run the simple KGAS MCP server"""
    print("🚀 Starting KGAS Simple MCP Server...")
    print(f"📁 Working from: {project_root}")
    
    # Test core components
    service_manager = get_service_manager()
    print(f"📊 Core Services: {'✅ Available' if service_manager else '❌ Unavailable'}")
    
    print("🎉 KGAS Simple MCP Server ready!")
    print("📋 Available tools:")
    print("   • test_kgas_tools - Test which tools are available")
    print("   • load_pdf_document - Load PDF documents")
    print("   • chunk_text - Break text into chunks")
    print("   • extract_entities_from_text - Extract named entities")
    print("   • calculate_pagerank - Calculate PageRank scores")
    print("   • query_graph - Query the knowledge graph")
    print("   • get_kgas_system_status - Get system status")
    
    # Run the MCP server
    mcp.run()


if __name__ == "__main__":
    main()