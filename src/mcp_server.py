"""Super-Digimon MCP Server

Main MCP server exposing the core services as tools.
Provides the foundation for the 121-tool GraphRAG system.

Currently implements:
- T107: Identity Service tools
- T110: Provenance Service tools  
- T111: Quality Service tools
- T121: Workflow State Service tools
"""

from fastmcp import FastMCP
from typing import Dict, List, Optional, Any
import os
from pathlib import Path

# Import core services and configuration
from src.core.service_manager import get_service_manager
from src.core.config import ConfigurationManager
from src.core.quality_service import QualityTier
from src.core.workflow_state_service import WorkflowStateService

# Import Phase 1 tools
from src.core.pipeline_orchestrator import PipelineOrchestrator
from src.core.tool_factory import create_unified_workflow_config, Phase, OptimizationLevel
from src.core.config import ConfigurationManager
from src.tools.phase1.phase1_mcp_tools import create_phase1_mcp_tools

# Initialize MCP server
mcp = FastMCP("super-digimon")

# Get shared service manager and configuration
service_manager = get_service_manager()
config_manager = ConfigurationManager()
config = config_manager.get_config()

# Use shared services from manager
identity_service = service_manager.identity_service
provenance_service = service_manager.provenance_service
quality_service = service_manager.quality_service

# Get workflow storage directory from configuration
workflow_storage = config.workflow.storage_dir if hasattr(config, 'workflow') else "./data/workflows"
workflow_service = WorkflowStateService(workflow_storage)

# Initialize pipeline orchestrator
config_manager_unified = ConfigManager()
unified_config = create_unified_workflow_config(
    phase=Phase.PHASE1,
    optimization_level=OptimizationLevel.STANDARD,
    workflow_storage_dir=workflow_storage
)
orchestrator = PipelineOrchestrator(unified_config, config_manager_unified)


# =============================================================================
# T107: Identity Service Tools
# =============================================================================

@mcp.tool()
def create_mention(
    surface_form: str,
    start_pos: int,
    end_pos: int,
    source_ref: str,
    entity_type: str = None,
    confidence: float = 0.8
) -> Dict[str, Any]:
    """Create a new mention and link to entity.
    
    Args:
        surface_form: Exact text as it appears
        start_pos: Start character position  
        end_pos: End character position
        source_ref: Reference to source document
        entity_type: Optional entity type hint
        confidence: Confidence score (0.0-1.0)
    """
    return identity_service.create_mention(
        surface_form=surface_form,
        start_pos=start_pos,
        end_pos=end_pos,
        source_ref=source_ref,
        entity_type=entity_type,
        confidence=confidence
    )


@mcp.tool()
def get_entity_by_mention(mention_id: str) -> Optional[Dict[str, Any]]:
    """Get entity associated with a mention.
    
    Args:
        mention_id: ID of the mention
    """
    return identity_service.get_entity_by_mention(mention_id)


@mcp.tool()
def get_mentions_for_entity(entity_id: str) -> List[Dict[str, Any]]:
    """Get all mentions for an entity.
    
    Args:
        entity_id: ID of the entity
    """
    return identity_service.get_mentions_for_entity(entity_id)


@mcp.tool()
def merge_entities(entity_id1: str, entity_id2: str) -> Dict[str, Any]:
    """Merge two entities (keeping the first one).
    
    Args:
        entity_id1: ID of entity to keep
        entity_id2: ID of entity to merge into first
    """
    return identity_service.merge_entities(entity_id1, entity_id2)


@mcp.tool()
def get_identity_stats() -> Dict[str, Any]:
    """Get identity service statistics."""
    return identity_service.get_stats()


# =============================================================================
# T110: Provenance Service Tools  
# =============================================================================

@mcp.tool()
def start_operation(
    tool_id: str,
    operation_type: str,
    inputs: List[str],
    parameters: Dict[str, Any] = None
) -> str:
    """Start tracking a new operation.
    
    Args:
        tool_id: Identifier of the tool performing operation
        operation_type: Type of operation (create, update, delete, query)
        inputs: List of input object references
        parameters: Tool parameters
    """
    return provenance_service.start_operation(
        tool_id=tool_id,
        operation_type=operation_type,
        inputs=inputs,
        parameters=parameters or {}
    )


@mcp.tool()
def complete_operation(
    operation_id: str,
    outputs: List[str],
    success: bool = True,
    error_message: str = None,
    metadata: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Complete an operation and record outputs.
    
    Args:
        operation_id: Operation to complete
        outputs: List of output object references
        success: Whether operation succeeded
        error_message: Error message if failed
        metadata: Additional metadata
    """
    return provenance_service.complete_operation(
        operation_id=operation_id,
        outputs=outputs,
        success=success,
        error_message=error_message,
        metadata=metadata
    )


@mcp.tool()
def get_lineage(object_ref: str, max_depth: int = 10) -> Dict[str, Any]:
    """Get the lineage chain for an object.
    
    Args:
        object_ref: Reference to object
        max_depth: Maximum depth to traverse
    """
    return provenance_service.get_lineage(object_ref, max_depth)


@mcp.tool()
def get_operation_details(operation_id: str) -> Optional[Dict[str, Any]]:
    """Get details of a specific operation.
    
    Args:
        operation_id: ID of operation
    """
    return provenance_service.get_operation(operation_id)


@mcp.tool()
def get_operations_for_object(object_ref: str) -> List[Dict[str, Any]]:
    """Get all operations that touched an object.
    
    Args:
        object_ref: Reference to object
    """
    return provenance_service.get_operations_for_object(object_ref)


@mcp.tool()
def get_tool_statistics() -> Dict[str, Any]:
    """Get statistics about tool usage."""
    return provenance_service.get_tool_statistics()


# =============================================================================
# T111: Quality Service Tools
# =============================================================================

@mcp.tool()
def assess_confidence(
    object_ref: str,
    base_confidence: float,
    factors: Dict[str, float] = None,
    metadata: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Assess and record confidence for an object.
    
    Args:
        object_ref: Reference to object being assessed
        base_confidence: Base confidence score (0.0-1.0)
        factors: Contributing factors to confidence
        metadata: Additional assessment metadata
    """
    return quality_service.assess_confidence(
        object_ref=object_ref,
        base_confidence=base_confidence,
        factors=factors,
        metadata=metadata
    )


@mcp.tool()
def propagate_confidence(
    input_refs: List[str],
    operation_type: str,
    boost_factor: float = 1.0
) -> float:
    """Propagate confidence from inputs through an operation.
    
    Args:
        input_refs: References to input objects
        operation_type: Type of operation being performed
        boost_factor: Factor to boost/reduce confidence
    """
    return quality_service.propagate_confidence(
        input_refs=input_refs,
        operation_type=operation_type,
        boost_factor=boost_factor
    )


@mcp.tool()
def get_quality_assessment(object_ref: str) -> Optional[Dict[str, Any]]:
    """Get quality assessment for an object.
    
    Args:
        object_ref: Reference to object
    """
    return quality_service.get_quality_assessment(object_ref)


@mcp.tool()
def get_confidence_trend(object_ref: str) -> Dict[str, Any]:
    """Get confidence trend for an object.
    
    Args:
        object_ref: Reference to object
    """
    return quality_service.get_confidence_trend(object_ref)


@mcp.tool()
def filter_by_quality(
    object_refs: List[str],
    min_tier: str = "LOW",
    min_confidence: float = 0.0
) -> List[str]:
    """Filter objects by quality criteria.
    
    Args:
        object_refs: List of object references to filter
        min_tier: Minimum quality tier (HIGH, MEDIUM, LOW)
        min_confidence: Minimum confidence score
    """
    tier_map = {
        "HIGH": QualityTier.HIGH,
        "MEDIUM": QualityTier.MEDIUM,
        "LOW": QualityTier.LOW
    }
    
    min_tier_enum = tier_map.get(min_tier, QualityTier.LOW)
    
    return quality_service.filter_by_quality(
        object_refs=object_refs,
        min_tier=min_tier_enum,
        min_confidence=min_confidence
    )


@mcp.tool()
def get_quality_statistics() -> Dict[str, Any]:
    """Get quality service statistics."""
    return quality_service.get_quality_statistics()


# =============================================================================
# T121: Workflow State Service Tools
# =============================================================================

@mcp.tool()
def start_workflow(
    name: str,
    total_steps: int,
    initial_state: Dict[str, Any] = None
) -> str:
    """Start a new workflow with tracking.
    
    Args:
        name: Human-readable workflow name
        total_steps: Expected total number of steps
        initial_state: Initial workflow state data
    """
    return workflow_service.start_workflow(
        name=name,
        total_steps=total_steps,
        initial_state=initial_state
    )


@mcp.tool()
def create_checkpoint(
    workflow_id: str,
    step_name: str,
    step_number: int,
    state_data: Dict[str, Any],
    metadata: Dict[str, Any] = None
) -> str:
    """Create a workflow checkpoint.
    
    Args:
        workflow_id: ID of the workflow
        step_name: Name of the current step
        step_number: Number of the current step
        state_data: Current workflow state
        metadata: Additional checkpoint metadata
    """
    return workflow_service.create_checkpoint(
        workflow_id=workflow_id,
        step_name=step_name,
        step_number=step_number,
        state_data=state_data,
        metadata=metadata
    )


@mcp.tool()
def restore_from_checkpoint(checkpoint_id: str) -> Dict[str, Any]:
    """Restore workflow state from a checkpoint.
    
    Args:
        checkpoint_id: ID of checkpoint to restore from
    """
    return workflow_service.restore_from_checkpoint(checkpoint_id)


@mcp.tool()
def update_workflow_progress(
    workflow_id: str,
    step_number: int,
    status: str = "running",
    error_message: str = None
) -> Dict[str, Any]:
    """Update workflow progress.
    
    Args:
        workflow_id: ID of workflow to update
        step_number: Current step number
        status: Workflow status (running, completed, failed, paused)
        error_message: Error message if failed
    """
    return workflow_service.update_workflow_progress(
        workflow_id=workflow_id,
        step_number=step_number,
        status=status,
        error_message=error_message
    )


@mcp.tool()
def get_workflow_status(workflow_id: str) -> Optional[Dict[str, Any]]:
    """Get current workflow status.
    
    Args:
        workflow_id: ID of workflow
    """
    return workflow_service.get_workflow_status(workflow_id)


@mcp.tool()
def get_workflow_checkpoints(workflow_id: str) -> List[Dict[str, Any]]:
    """Get all checkpoints for a workflow.
    
    Args:
        workflow_id: ID of workflow
    """
    return workflow_service.get_workflow_checkpoints(workflow_id)


@mcp.tool()
def get_workflow_statistics() -> Dict[str, Any]:
    """Get workflow service statistics."""
    return workflow_service.get_service_statistics()


# =============================================================================
# Phase 1: Vertical Slice Tools
# =============================================================================

@mcp.tool()
def execute_pdf_to_answer_workflow(
    document_paths: List[str],
    query: str,
    workflow_name: str = "PDF_Analysis"
) -> Dict[str, Any]:
    """Execute complete PDF → PageRank → Answer workflow.
    
    Args:
        document_paths: List of document file paths to process
        query: Question to answer using the extracted graph
        workflow_name: Name for workflow tracking
    """
    return orchestrator.execute(document_paths=document_paths, queries=[query])


@mcp.tool()
def get_orchestrator_info() -> Dict[str, Any]:
    """Get information about the pipeline orchestrator."""
    return orchestrator.get_execution_stats()


# =============================================================================
# System Tools
# =============================================================================

@mcp.tool()
def test_connection() -> str:
    """Test MCP server connection."""
    return "✅ Super-Digimon MCP Server Connected!"


@mcp.tool()
def echo(message: str) -> str:
    """Echo back a message."""
    return f"Echo: {message}"


@mcp.tool()
def get_system_status() -> Dict[str, Any]:
    """Get overall system status."""
    return {
        "status": "operational",
        "services": {
            "identity_service": "active",
            "provenance_service": "active", 
            "quality_service": "active",
            "workflow_service": "active",
            "pipeline_orchestrator": "active",
            "phase1_pipeline": "active"
        },
        "core_services_count": 4,
        "phase1_tools_count": 33,  # Updated count: 8 existing + 25 new pipeline tools
        "orchestrator_ready": True,
        "server_name": "super-digimon"
    }


# Add Phase 1 pipeline tools to the server
create_phase1_mcp_tools(mcp)

if __name__ == "__main__":
    mcp.run()