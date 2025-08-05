#!/usr/bin/env python3
"""
Register all available tools for natural language workflow generation.

This script populates the global tool registry with all available KGAS tools
so the WorkflowAgent can discover and use them in generated workflows.
"""

import logging
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.core.tool_adapter import register_all_mvrt_tools
from src.core.tool_contract import get_tool_registry
from src.core.service_manager import ServiceManager
from src.core.tool_factory import ToolFactory
from src.core.tool_discovery_service import ToolDiscoveryService

logger = logging.getLogger(__name__)


def register_phase1_tools(service_manager: ServiceManager):
    """Register Phase 1 foundation tools."""
    from src.tools.phase1.t01_pdf_loader_unified import T01PDFLoaderUnified
    from src.tools.phase1.t15a_text_chunker_unified import T15ATextChunkerUnified
    # T23a and T27 are deprecated - use T23c instead
    from src.tools.phase1.t31_entity_builder_unified import T31EntityBuilderUnified
    from src.tools.phase1.t34_edge_builder_unified import T34EdgeBuilderUnified
    from src.tools.phase1.t49_multihop_query_unified import T49MultiHopQueryUnified
    from src.tools.phase1.t68_pagerank_unified import T68PageRankCalculatorUnified
    from src.core.tool_adapter import LegacyToolAdapter
    
    registry = get_tool_registry()
    
    # Tool definitions with IDs and names
    # Note: T23a and T27 are deprecated in favor of T23c which does both entity + relationship extraction
    tool_definitions = [
        (T01PDFLoaderUnified(service_manager), "T01_PDF_LOADER", "PDF Loader"),
        (T15ATextChunkerUnified(service_manager), "T15A_TEXT_CHUNKER", "Text Chunker"),
        (T31EntityBuilderUnified(service_manager), "T31_ENTITY_BUILDER", "Entity Builder"),
        (T34EdgeBuilderUnified(service_manager), "T34_EDGE_BUILDER", "Edge Builder"),
        (T49MultiHopQueryUnified(service_manager), "T49_MULTIHOP_QUERY", "Multi-hop Query"),
        (T68PageRankCalculatorUnified(service_manager), "T68_PAGERANK", "PageRank Calculator")
    ]
    
    # Register each tool
    registered_count = 0
    for tool_instance, tool_id, tool_name in tool_definitions:
        try:
            # Create adapter for legacy tool
            adapter = LegacyToolAdapter(tool_instance, tool_id, tool_name)
            registry.register_tool(adapter)
            logger.info(f"Registered {tool_id} via LegacyToolAdapter")
            registered_count += 1
        except Exception as e:
            logger.error(f"Failed to register {tool_id}: {e}")
    
    return registered_count


def register_phase2_tools(service_manager: ServiceManager):
    """Register Phase 2 advanced analysis tools."""
    from src.tools.phase2.t23c_ontology_aware_extractor_unified import OntologyAwareExtractor
    from src.tools.phase2.t50_community_detection_unified import CommunityDetectionTool
    from src.tools.phase2.t51_centrality_analysis_unified import CentralityAnalysisTool
    from src.tools.phase2.t52_graph_clustering_unified import GraphClusteringTool
    from src.tools.phase2.t53_network_motifs_unified import NetworkMotifsTool
    from src.tools.phase2.t54_graph_visualization_unified import GraphVisualizationTool
    from src.tools.phase2.t55_temporal_analysis_unified import TemporalAnalysisTool
    from src.tools.phase2.t56_graph_metrics_unified import GraphMetricsTool
    from src.tools.phase2.t57_path_analysis_unified import PathAnalysisTool
    from src.core.tool_adapter import LegacyToolAdapter
    
    registry = get_tool_registry()
    
    # Tool definitions with IDs and names
    tool_definitions = [
        (OntologyAwareExtractor(service_manager), "T23C_ONTOLOGY_AWARE_EXTRACTOR", "Ontology-Aware Entity Extractor"),
        (CommunityDetectionTool(service_manager), "T50_COMMUNITY_DETECTION", "Community Detection"),
        (CentralityAnalysisTool(service_manager), "T51_CENTRALITY_ANALYSIS", "Centrality Analysis"),
        (GraphClusteringTool(service_manager), "T52_GRAPH_CLUSTERING", "Graph Clustering"),
        (NetworkMotifsTool(service_manager), "T53_NETWORK_MOTIFS", "Network Motifs Detection"),
        (GraphVisualizationTool(service_manager), "T54_GRAPH_VISUALIZATION", "Graph Visualization"),
        (TemporalAnalysisTool(service_manager), "T55_TEMPORAL_ANALYSIS", "Temporal Analysis"),
        (GraphMetricsTool(service_manager), "T56_GRAPH_METRICS", "Graph Metrics Calculator"),
        (PathAnalysisTool(service_manager), "T57_PATH_ANALYSIS", "Path Analysis")
    ]
    
    # Register each tool
    registered_count = 0
    for tool_instance, tool_id, tool_name in tool_definitions:
        try:
            # Create adapter for legacy tool
            adapter = LegacyToolAdapter(tool_instance, tool_id, tool_name)
            registry.register_tool(adapter)
            logger.info(f"Registered {tool_id} via LegacyToolAdapter")
            registered_count += 1
        except Exception as e:
            logger.error(f"Failed to register {tool_id}: {e}")
    
    return registered_count


def register_cross_modal_tools(service_manager: ServiceManager):
    """Register cross-modal conversion tools."""
    from src.tools.cross_modal.graph_table_exporter import GraphTableExporter
    # TableVectorEmbedder doesn't exist yet - use T15b_vector_embedder from phase1
    from src.tools.phase1.t15b_vector_embedder import VectorEmbedder
    from src.core.tool_adapter import LegacyToolAdapter
    
    registry = get_tool_registry()
    
    # Tool definitions with IDs and names
    tool_definitions = [
        (GraphTableExporter(), "T91_GRAPH_TABLE_EXPORTER", "Graph to Table Exporter"),
        (VectorEmbedder(service_manager), "T15B_VECTOR_EMBEDDER", "Vector Embedder")
    ]
    
    # Register each tool
    registered_count = 0
    for tool_instance, tool_id, tool_name in tool_definitions:
        try:
            # Create adapter for legacy tool
            adapter = LegacyToolAdapter(tool_instance, tool_id, tool_name)
            registry.register_tool(adapter)
            logger.info(f"Registered {tool_id} via LegacyToolAdapter")
            registered_count += 1
        except Exception as e:
            logger.error(f"Failed to register {tool_id}: {e}")
    
    return registered_count


def register_all_tools():
    """Register all available tools for workflow generation."""
    logging.basicConfig(level=logging.INFO)
    
    # Initialize service manager
    service_manager = ServiceManager()
    
    # Try auto-registration first
    logger.info("Attempting auto-registration of MVRT tools...")
    try:
        register_all_mvrt_tools()
        logger.info("Auto-registration completed")
    except Exception as e:
        logger.error(f"Auto-registration failed: {e}")
    
    # Manual registration of key tools
    logger.info("Registering Phase 1 tools...")
    phase1_count = register_phase1_tools(service_manager)
    
    logger.info("Registering Phase 2 tools...")
    phase2_count = register_phase2_tools(service_manager)
    
    logger.info("Registering cross-modal tools...")
    cross_modal_count = register_cross_modal_tools(service_manager)
    
    # Check registry status
    registry = get_tool_registry()
    registered_tools = registry.list_tools()
    
    logger.info(f"Total tools registered: {len(registered_tools)}")
    logger.info(f"Registered tool IDs: {registered_tools}")
    
    # Categorize tools
    graph_tools = registry.get_tools_by_category('graph')
    table_tools = registry.get_tools_by_category('table')
    vector_tools = registry.get_tools_by_category('vector')
    cross_modal = registry.get_tools_by_category('cross_modal')
    
    logger.info(f"Graph tools: {len(graph_tools)}")
    logger.info(f"Table tools: {len(table_tools)}")
    logger.info(f"Vector tools: {len(vector_tools)}")
    logger.info(f"Cross-modal tools: {len(cross_modal)}")
    
    return registered_tools


if __name__ == "__main__":
    tools = register_all_tools()
    print(f"\nSuccessfully registered {len(tools)} tools for workflow generation")
    print("\nTools available for natural language workflows:")
    for tool_id in sorted(tools):
        print(f"  - {tool_id}")