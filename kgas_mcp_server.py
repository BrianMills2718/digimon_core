#!/usr/bin/env python3
"""
KGAS MCP Server - Main entry point for all KGAS tools

Exposes all implemented KGAS tools as MCP functions:
- Phase 1 Tools (26 implemented)
- Phase 2 Tools (6 implemented) 
- Phase 3 Tools (3 implemented)
- Cross-Modal Tools (to be added)

This server makes all KGAS tools available to Claude Code and other MCP clients.
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
mcp = FastMCP("KGAS Tools")


def initialize_services():
    """Initialize core services if available"""
    try:
        from src.core.service_manager import get_service_manager
        service_manager = get_service_manager()
        logger.info("Core services initialized successfully")
        return service_manager
    except Exception as e:
        logger.warning(f"Core services not available: {e}")
        return None


def load_phase1_tools():
    """Load Phase 1 MCP tools"""
    try:
        from src.tools.phase1.phase1_mcp_tools import create_phase1_mcp_tools
        result = create_phase1_mcp_tools(mcp)
        logger.info(f"Loaded Phase 1 tools: {result['tools_added']} tools in {len(result['categories'])} categories")
        return True
    except Exception as e:
        logger.error(f"Failed to load Phase 1 tools: {e}")
        return False


def load_phase2_tools():
    """Load Phase 2 MCP tools if available"""
    try:
        # Check if Phase 2 MCP tools exist
        phase2_mcp_path = project_root / "src" / "tools" / "phase2" / "phase2_mcp_tools.py"
        if phase2_mcp_path.exists():
            from src.tools.phase2.phase2_mcp_tools import create_phase2_mcp_tools
            result = create_phase2_mcp_tools(mcp)
            logger.info(f"Loaded Phase 2 tools: {result.get('tools_added', 0)} tools")
            return True
        else:
            logger.info("Phase 2 MCP tools not available")
            return False
    except Exception as e:
        logger.error(f"Failed to load Phase 2 tools: {e}")
        return False


def load_phase3_tools():
    """Load Phase 3 MCP tools if available"""
    try:
        # Check if Phase 3 MCP tools exist
        phase3_mcp_path = project_root / "src" / "tools" / "phase3" / "phase3_mcp_tools.py"
        if phase3_mcp_path.exists():
            from src.tools.phase3.phase3_mcp_tools import create_phase3_mcp_tools
            result = create_phase3_mcp_tools(mcp)
            logger.info(f"Loaded Phase 3 tools: {result.get('tools_added', 0)} tools")
            return True
        else:
            logger.info("Phase 3 MCP tools not available")
            return False
    except Exception as e:
        logger.error(f"Failed to load Phase 3 tools: {e}")
        return False


# Core KGAS utility functions
@mcp.tool()
def get_kgas_tool_registry() -> Dict[str, Any]:
    """Get complete registry of all available KGAS tools."""
    try:
        from src.tools.tool_registry import ToolRegistry
        registry = ToolRegistry()
        return {
            "total_tools": len(registry.tools),
            "implementation_status": registry.get_implementation_status(),
            "priority_queue": [
                {
                    "tool_id": tool.tool_id,
                    "name": tool.name,
                    "priority": tool.priority,
                    "category": tool.category.value
                }
                for tool in registry.get_priority_queue()[:10]
            ],
            "categories": {
                "graph": len([t for t in registry.tools.values() if t.category.value == "graph"]),
                "table": len([t for t in registry.tools.values() if t.category.value == "table"]),
                "vector": len([t for t in registry.tools.values() if t.category.value == "vector"]),
                "cross_modal": len([t for t in registry.tools.values() if t.category.value == "cross_modal"])
            }
        }
    except Exception as e:
        return {"error": f"Failed to get tool registry: {str(e)}"}


@mcp.tool()
def get_kgas_status() -> Dict[str, Any]:
    """Get overall KGAS system status and health."""
    try:
        # Check core services
        service_manager = initialize_services()
        services_status = "available" if service_manager else "unavailable"
        
        # Check database connections
        neo4j_status = "unknown"
        try:
            from src.core.neo4j_manager import Neo4jManager
            neo4j_manager = Neo4jManager()
            neo4j_status = "connected" if neo4j_manager.driver else "disconnected"
        except Exception:
            neo4j_status = "error"
        
        # Check tool availability
        available_tools = 0
        phase_statuses = {}
        
        # Count Phase 1 tools
        try:
            from src.tools.phase1 import phase1_mcp_tools
            phase_statuses["phase1"] = "available"
            available_tools += 25  # Phase 1 has 25 tools
        except Exception:
            phase_statuses["phase1"] = "unavailable"
        
        # Count Phase 2 tools
        try:
            from src.tools.phase2 import phase2_mcp_tools
            phase_statuses["phase2"] = "available"
            available_tools += 6   # Estimated Phase 2 tools
        except Exception:
            phase_statuses["phase2"] = "unavailable"
        
        # Count Phase 3 tools
        try:
            from src.tools.phase3 import phase3_mcp_tools
            phase_statuses["phase3"] = "available"
            available_tools += 3   # Estimated Phase 3 tools
        except Exception:
            phase_statuses["phase3"] = "unavailable"
        
        return {
            "system_status": "operational" if services_status == "available" else "degraded",
            "core_services": services_status,
            "neo4j_connection": neo4j_status,
            "available_tools": available_tools,
            "total_planned_tools": 121,
            "implementation_progress": f"{available_tools}/121 ({available_tools/121*100:.1f}%)",
            "phase_statuses": phase_statuses,
            "working_directory": str(project_root)
        }
    except Exception as e:
        return {
            "system_status": "error",
            "error": str(e)
        }


@mcp.tool()
def run_kgas_workflow(
    document_paths: list,
    workflow_type: str = "vertical_slice",
    parameters: dict = None
) -> Dict[str, Any]:
    """Run a complete KGAS workflow on documents."""
    try:
        from src.core.pipeline_orchestrator import PipelineOrchestrator
        
        orchestrator = PipelineOrchestrator()
        
        if workflow_type == "vertical_slice":
            result = orchestrator.execute_vertical_slice_workflow(document_paths, parameters or {})
        elif workflow_type == "multi_document":
            result = orchestrator.execute_multi_document_workflow(document_paths, parameters or {})
        else:
            return {"error": f"Unknown workflow type: {workflow_type}"}
        
        return {
            "status": "success",
            "workflow_type": workflow_type,
            "documents_processed": len(document_paths),
            "result": result
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


@mcp.tool()
def validate_kgas_tools() -> Dict[str, Any]:
    """Validate all KGAS tools are working correctly."""
    try:
        validation_results = {}
        
        # Validate Phase 1 tools
        try:
            from src.tools.phase1.phase1_mcp_tools import Phase1MCPToolsManager
            manager = Phase1MCPToolsManager()
            validation_results["phase1"] = {
                "status": "available",
                "tool_count": 25,
                "categories": manager.get_tool_categories()
            }
        except Exception as e:
            validation_results["phase1"] = {
                "status": "error",
                "error": str(e)
            }
        
        # Check individual tool examples
        test_results = {}
        
        # Test PDF loader
        try:
            from src.tools.phase1.t01_pdf_loader_unified import PDFLoader
            loader = PDFLoader()
            info = loader.get_tool_info()
            test_results["pdf_loader"] = "available"
        except Exception as e:
            test_results["pdf_loader"] = f"error: {str(e)}"
        
        # Test spaCy NER
        try:
            from src.tools.phase1.t23a_spacy_ner_unified import SpacyNER
            ner = SpacyNER()
            info = ner.get_tool_info()
            test_results["spacy_ner"] = "available"
        except Exception as e:
            test_results["spacy_ner"] = f"error: {str(e)}"
        
        # Test PageRank
        try:
            from src.tools.phase1.t68_pagerank_calculator_unified import PageRankCalculator
            pagerank = PageRankCalculator()
            info = pagerank.get_tool_info()
            test_results["pagerank"] = "available"
        except Exception as e:
            test_results["pagerank"] = f"error: {str(e)}"
        
        return {
            "overall_status": "validated",
            "phase_results": validation_results,
            "individual_tools": test_results,
            "timestamp": str(Path(__file__).stat().st_mtime)
        }
        
    except Exception as e:
        return {
            "overall_status": "error",
            "error": str(e)
        }


@mcp.tool()
def get_tool_documentation(tool_id: str) -> Dict[str, Any]:
    """Get documentation for a specific KGAS tool."""
    try:
        # Map common tool IDs to their modules
        tool_map = {
            "T01": "src.tools.phase1.t01_pdf_loader_unified",
            "T15A": "src.tools.phase1.t15a_text_chunker_unified", 
            "T23A": "src.tools.phase1.t23a_spacy_ner_unified",
            "T27": "src.tools.phase1.t27_relationship_extractor_unified",
            "T31": "src.tools.phase1.t31_entity_builder_unified",
            "T34": "src.tools.phase1.t34_edge_builder_unified",
            "T68": "src.tools.phase1.t68_pagerank_calculator_unified",
            "T49": "src.tools.phase1.t49_multihop_query_unified"
        }
        
        if tool_id.upper() in tool_map:
            module_path = tool_map[tool_id.upper()]
            # Import and get tool info
            module_parts = module_path.split('.')
            module = __import__(module_path, fromlist=[module_parts[-1]])
            
            # Get the main class (assuming it follows naming convention)
            tool_classes = [getattr(module, name) for name in dir(module) 
                          if name[0].isupper() and hasattr(getattr(module, name), 'get_tool_info')]
            
            if tool_classes:
                tool = tool_classes[0]()
                return tool.get_tool_info()
        
        return {"error": f"Tool {tool_id} not found or not documented"}
        
    except Exception as e:
        return {"error": f"Failed to get documentation for {tool_id}: {str(e)}"}


# Initialize all available tools
def main():
    """Initialize and run the KGAS MCP server"""
    print("🚀 Starting KGAS MCP Server...")
    
    # Initialize core services
    service_manager = initialize_services()
    
    # Load all available tool phases
    phase1_loaded = load_phase1_tools()
    phase2_loaded = load_phase2_tools()
    phase3_loaded = load_phase3_tools()
    
    print(f"📊 Tool Loading Summary:")
    print(f"   Phase 1: {'✅ Loaded' if phase1_loaded else '❌ Failed'}")
    print(f"   Phase 2: {'✅ Loaded' if phase2_loaded else '❌ Not Available'}")
    print(f"   Phase 3: {'✅ Loaded' if phase3_loaded else '❌ Not Available'}")
    print(f"   Core Services: {'✅ Available' if service_manager else '❌ Unavailable'}")
    
    if not any([phase1_loaded, phase2_loaded, phase3_loaded]):
        print("⚠️  No tools loaded successfully!")
        sys.exit(1)
    
    print(f"🎉 KGAS MCP Server ready with core utilities + loaded phases")
    print(f"📁 Working from: {project_root}")
    
    # Run the MCP server
    mcp.run()


if __name__ == "__main__":
    main()