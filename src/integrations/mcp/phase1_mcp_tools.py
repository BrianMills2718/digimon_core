"""Phase 1 MCP Tools - Simplified Access to Internal Tools

Provides access to the 47 internal tools without requiring MCP server setup.
"""

from typing import List, Any
from src.core.service_manager import get_service_manager

# Import Phase 1 tools
from src.tools.phase1.t01_pdf_loader_unified import T01PDFLoaderUnified
from src.tools.phase1.t15a_text_chunker_unified import T15ATextChunkerUnified  
from src.tools.phase1.t23a_spacy_ner_unified import T23ASpacyNERUnified
from src.tools.phase1.t27_relationship_extractor_unified import T27RelationshipExtractorUnified
from src.tools.phase1.t31_entity_builder_unified import T31EntityBuilderUnified
from src.tools.phase1.t34_edge_builder_unified import T34EdgeBuilderUnified


def create_phase1_mcp_tools() -> List[Any]:
    """Create Phase 1 tools without MCP server requirement"""
    
    # Get shared service manager
    service_manager = get_service_manager()
    
    # Initialize core Phase 1 tools
    tools = []
    
    try:
        pdf_loader = T01PDFLoaderUnified(service_manager)
        tools.append(pdf_loader)
    except Exception as e:
        print(f"Warning: Could not create PDF loader: {e}")
    
    try:
        text_chunker = T15ATextChunkerUnified(service_manager)
        tools.append(text_chunker)
    except Exception as e:
        print(f"Warning: Could not create text chunker: {e}")
    
    try:
        entity_extractor = T23ASpacyNERUnified(service_manager)
        tools.append(entity_extractor)
    except Exception as e:
        print(f"Warning: Could not create entity extractor: {e}")
    
    try:
        relationship_extractor = T27RelationshipExtractorUnified(service_manager)
        tools.append(relationship_extractor)
    except Exception as e:
        print(f"Warning: Could not create relationship extractor: {e}")
    
    try:
        entity_builder = T31EntityBuilderUnified(service_manager)
        tools.append(entity_builder)
    except Exception as e:
        print(f"Warning: Could not create entity builder: {e}")
    
    try:
        edge_builder = T34EdgeBuilderUnified(service_manager)
        tools.append(edge_builder)
    except Exception as e:
        print(f"Warning: Could not create edge builder: {e}")
    
    return tools


def get_available_tools() -> List[str]:
    """Get list of available tool IDs"""
    tools = create_phase1_mcp_tools()
    return [getattr(tool, 'tool_id', type(tool).__name__) for tool in tools]


def get_tool_count() -> int:
    """Get count of available tools"""
    return len(create_phase1_mcp_tools())


if __name__ == "__main__":
    tools = create_phase1_mcp_tools()
    print(f"Created {len(tools)} internal tools")
    for i, tool in enumerate(tools):
        print(f"{i+1}. {type(tool).__name__}")