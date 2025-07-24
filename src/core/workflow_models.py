"""
Workflow models and data structures for enhanced PipelineOrchestrator.

This module defines the data structures used by the PipelineOrchestrator
for managing research workflows with service coordination.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class WorkflowStatus(Enum):
    """Workflow execution status."""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    COMPLETED_WITH_WARNINGS = "completed_with_warnings"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ServiceStatus(Enum):
    """Service health status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class WorkflowSpec:
    """Specification for a research workflow."""
    documents: List[Dict[str, str]]
    analysis_modes: List[str] = field(default_factory=lambda: ['graph', 'table', 'vector'])
    theory_integration: bool = True
    quality_validation: bool = True
    concurrent_processing: bool = False
    checkpoint_interval: int = 5  # Checkpoint every N steps
    max_retries: int = 3
    timeout_seconds: Optional[int] = None


@dataclass
class DocumentResult:
    """Result of processing a single document."""
    document_id: str
    analysis_modes: List[str]
    cross_modal_preserved: bool
    theory_extracted: bool
    quality_score: float
    processing_time: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowResult:
    """Result of a complete workflow execution."""
    workflow_id: str
    status: str
    analysis_results: List[DocumentResult]
    overall_quality_score: float
    start_time: datetime
    end_time: datetime
    duration: float
    services_used: List[str]
    service_health: Dict[str, Dict[str, Any]]
    warnings: List[str] = field(default_factory=list)
    recovered_errors: List[Dict[str, Any]] = field(default_factory=list)
    resumed_from_checkpoint: bool = False
    checkpoint_id: Optional[str] = None
    retry_count: int = 0


@dataclass
class ServiceHealthStatus:
    """Health status of a service."""
    service_name: str
    status: ServiceStatus
    last_check: datetime
    response_time_ms: float
    error_rate: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowCheckpoint:
    """Checkpoint for workflow state persistence."""
    checkpoint_id: str
    workflow_id: str
    timestamp: datetime
    processed_documents: int
    state_data: Dict[str, Any]
    service_states: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)