"""
Workflow Configuration

Manages workflow configuration for different phases and optimization levels.
"""

from enum import Enum
from typing import Dict, Any
from datetime import datetime


class Phase(Enum):
    """Workflow phase enumeration"""
    PHASE1 = "phase1"
    PHASE2 = "phase2"
    PHASE3 = "phase3"


class OptimizationLevel(Enum):
    """Optimization level enumeration"""
    MINIMAL = "minimal"
    STANDARD = "standard"
    PERFORMANCE = "performance"
    COMPREHENSIVE = "comprehensive"


def create_unified_workflow_config(phase: Phase = Phase.PHASE1, 
                                  optimization_level: OptimizationLevel = OptimizationLevel.STANDARD) -> Dict[str, Any]:
    """Create a unified workflow configuration for the specified phase and optimization level."""
    base_config: Dict[str, Any] = {
        "phase": phase.value,
        "optimization_level": optimization_level.value,
        "created_at": datetime.now().isoformat(),
        "tools": [],
        "services": {
            "neo4j": True,
            "identity_service": True,
            "quality_service": True,
            "provenance_service": True
        }
    }
    
    # Phase-specific configuration
    if phase == Phase.PHASE1:
        base_config.update({
            "description": "Phase 1: Basic entity extraction and graph construction",
            "tools": [
                "t01_pdf_loader",
                "t15a_text_chunker",
                "t23a_spacy_ner",
                "t27_relationship_extractor",
                "t31_entity_builder",
                "t34_edge_builder",
                "t49_multihop_query",
                "t68_pagerank"
            ],
            "capabilities": {
                "document_processing": True,
                "entity_extraction": True,
                "relationship_extraction": True,
                "graph_construction": True,
                "basic_queries": True
            }
        })
    elif phase == Phase.PHASE2:
        base_config.update({
            "description": "Phase 2: Enhanced processing with ontology awareness",
            "tools": [
                "t23c_ontology_aware_extractor",
                "t31_ontology_graph_builder",
                "async_multi_document_processor"
            ],
            "capabilities": {
                "ontology_aware_extraction": True,
                "enhanced_graph_building": True,
                "multi_document_processing": True,
                "async_processing": True
            }
        })
    elif phase == Phase.PHASE3:
        base_config.update({
            "description": "Phase 3: Advanced multi-document fusion",
            "tools": [
                "t301_multi_document_fusion",
                "basic_multi_document_workflow"
            ],
            "capabilities": {
                "multi_document_fusion": True,
                "cross_document_entity_resolution": True,
                "conflict_resolution": True,
                "advanced_workflows": True
            }
        })
    
    # Optimization level adjustments
    if optimization_level == OptimizationLevel.MINIMAL:
        base_config["performance"] = {
            "batch_size": 5,
            "concurrency": 1,
            "timeout": 30,
            "memory_limit": "1GB"
        }
    elif optimization_level == OptimizationLevel.STANDARD:
        base_config["performance"] = {
            "batch_size": 10,
            "concurrency": 2,
            "timeout": 60,
            "memory_limit": "2GB"
        }
    elif optimization_level == OptimizationLevel.PERFORMANCE:
        base_config["performance"] = {
            "batch_size": 20,
            "concurrency": 4,
            "timeout": 120,
            "memory_limit": "4GB"
        }
    elif optimization_level == OptimizationLevel.COMPREHENSIVE:
        base_config["performance"] = {
            "batch_size": 50,
            "concurrency": 8,
            "timeout": 300,
            "memory_limit": "8GB"
        }
    
    return base_config
