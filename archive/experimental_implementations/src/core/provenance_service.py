"""T110: Provenance Service - Complete operation lineage tracking."""

import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

from ..models import ProvenanceRecord
from ..utils.database import DatabaseManager


logger = logging.getLogger(__name__)


class ProvenanceService:
    """
    T110: Provenance Service
    
    Tracks complete lineage of all operations in the system.
    Enables traceability, debugging, and quality assessment.
    """
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self._active_operations: Dict[str, ProvenanceRecord] = {}
        self._operation_stack: List[str] = []
    
    def start_operation(
        self,
        operation_type: str,
        tool_id: str,
        input_refs: List[str],
        parameters: Dict[str, Any]
    ) -> str:
        """Start tracking a new operation."""
        # Create provenance record
        record = ProvenanceRecord(
            operation_type=operation_type,
            tool_id=tool_id,
            input_refs=input_refs,
            parameters=parameters,
            status="running",
            parent_id=self._operation_stack[-1] if self._operation_stack else None
        )
        
        # Store in active operations
        self._active_operations[record.id] = record
        self._operation_stack.append(record.id)
        
        # Save initial state
        self.db.sqlite.save_provenance(record)
        
        logger.debug(f"Started operation: {record.id} ({operation_type})")
        return record.id
    
    def complete_operation(
        self,
        operation_id: str,
        output_refs: List[str],
        metrics: Optional[Dict[str, Any]] = None,
        confidence: float = 1.0
    ) -> ProvenanceRecord:
        """Mark an operation as completed."""
        if operation_id not in self._active_operations:
            raise ValueError(f"Operation not found: {operation_id}")
        
        record = self._active_operations[operation_id]
        record.output_refs = output_refs
        record.metrics = metrics or {}
        record.confidence = confidence
        record.status = "completed"
        record.duration_ms = int(
            (datetime.utcnow() - record.created_at).total_seconds() * 1000
        )
        record.updated_at = datetime.utcnow()
        
        # Update in database
        self.db.sqlite.update_provenance(record)
        
        # Clean up
        del self._active_operations[operation_id]
        if self._operation_stack and self._operation_stack[-1] == operation_id:
            self._operation_stack.pop()
        
        logger.debug(f"Completed operation: {operation_id} in {record.duration_ms}ms")
        return record
    
    def fail_operation(
        self,
        operation_id: str,
        error_message: str,
        partial_outputs: Optional[List[str]] = None
    ) -> ProvenanceRecord:
        """Mark an operation as failed."""
        if operation_id not in self._active_operations:
            raise ValueError(f"Operation not found: {operation_id}")
        
        record = self._active_operations[operation_id]
        record.status = "failed"
        record.error_message = error_message
        record.output_refs = partial_outputs or []
        record.confidence = 0.0
        record.quality_tier = "low"
        record.warnings.append(f"Operation failed: {error_message}")
        record.duration_ms = int(
            (datetime.utcnow() - record.created_at).total_seconds() * 1000
        )
        record.updated_at = datetime.utcnow()
        
        # Update in database
        self.db.sqlite.update_provenance(record)
        
        # Clean up
        del self._active_operations[operation_id]
        if self._operation_stack and self._operation_stack[-1] == operation_id:
            self._operation_stack.pop()
        
        logger.error(f"Failed operation: {operation_id} - {error_message}")
        return record
    
    def track_operation(
        self,
        operation_type: str,
        tool_id: str,
        input_refs: List[str],
        output_refs: List[str],
        parameters: Dict[str, Any],
        status: str = "success",
        confidence: float = 1.0,
        duration_ms: int = 0,
        error_message: Optional[str] = None
    ) -> ProvenanceRecord:
        """Track a complete operation (simplified API for tools)."""
        # Create provenance record
        record = ProvenanceRecord(
            operation_type=operation_type,
            tool_id=tool_id,
            input_refs=input_refs,
            output_refs=output_refs,
            parameters=parameters,
            status=status,
            confidence=confidence,
            duration_ms=duration_ms,
            error_message=error_message
        )
        
        # Save to database
        self.db.sqlite.save_provenance(record)
        
        logger.debug(f"Tracked operation: {record.id} ({operation_type})")
        return record
    
    def get_lineage(
        self,
        reference: str,
        direction: str = "backward",
        max_depth: int = 10
    ) -> List[ProvenanceRecord]:
        """Get lineage of an object (backward = sources, forward = derivatives)."""
        visited = set()
        lineage = []
        
        def trace_backward(ref: str, depth: int):
            if depth >= max_depth or ref in visited:
                return
            visited.add(ref)
            
            # Find operations that produced this reference
            records = self.db.sqlite.get_provenance_by_output(ref)
            for record in records:
                lineage.append(record)
                # Trace inputs
                for input_ref in record.input_refs:
                    trace_backward(input_ref, depth + 1)
        
        def trace_forward(ref: str, depth: int):
            if depth >= max_depth or ref in visited:
                return
            visited.add(ref)
            
            # Find operations that used this reference as input
            records = self.db.sqlite.get_provenance_by_input(ref)
            for record in records:
                lineage.append(record)
                # Trace outputs
                for output_ref in record.output_refs:
                    trace_forward(output_ref, depth + 1)
        
        if direction == "backward":
            trace_backward(reference, 0)
        elif direction == "forward":
            trace_forward(reference, 0)
        else:
            raise ValueError(f"Invalid direction: {direction}")
        
        # Sort by creation time
        lineage.sort(key=lambda r: r.created_at)
        return lineage
    
    def get_operation_chain(self, operation_id: str) -> List[ProvenanceRecord]:
        """Get the complete chain of operations leading to this one."""
        chain = []
        current_id = operation_id
        
        while current_id:
            record = self.db.sqlite.get_provenance(current_id)
            if not record:
                break
            chain.append(record)
            current_id = record.parent_id
        
        chain.reverse()  # Oldest first
        return chain
    
    def calculate_derived_confidence(self, reference: str) -> float:
        """Calculate confidence based on provenance chain."""
        lineage = self.get_lineage(reference, direction="backward", max_depth=20)
        
        if not lineage:
            return 1.0  # No provenance = assume original data
        
        # Multiply confidence through the chain
        confidence = 1.0
        for record in lineage:
            confidence *= record.confidence
        
        return confidence
    
    def get_statistics(
        self,
        tool_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get operation statistics."""
        records = self.db.sqlite.get_provenance_records(
            tool_id=tool_id,
            start_time=start_time,
            end_time=end_time
        )
        
        if not records:
            return {
                "total_operations": 0,
                "successful": 0,
                "failed": 0,
                "average_duration_ms": 0,
                "average_confidence": 0,
                "by_tool": {},
                "by_operation": {}
            }
        
        # Calculate statistics
        total = len(records)
        successful = sum(1 for r in records if r.status == "completed")
        failed = sum(1 for r in records if r.status == "failed")
        
        durations = [r.duration_ms for r in records if r.duration_ms > 0]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        confidences = [r.confidence for r in records if r.status == "completed"]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        # Group by tool and operation
        by_tool: Dict[str, int] = {}
        by_operation: Dict[str, int] = {}
        
        for record in records:
            by_tool[record.tool_id] = by_tool.get(record.tool_id, 0) + 1
            by_operation[record.operation_type] = by_operation.get(record.operation_type, 0) + 1
        
        return {
            "total_operations": total,
            "successful": successful,
            "failed": failed,
            "average_duration_ms": avg_duration,
            "average_confidence": avg_confidence,
            "by_tool": by_tool,
            "by_operation": by_operation
        }
    
    def export_lineage_graph(self, reference: str) -> Dict[str, Any]:
        """Export lineage as a graph structure for visualization."""
        lineage = self.get_lineage(reference, direction="backward", max_depth=50)
        
        nodes = []
        edges = []
        
        # Create nodes for operations
        for record in lineage:
            nodes.append({
                "id": record.id,
                "type": "operation",
                "label": f"{record.tool_id}:{record.operation_type}",
                "status": record.status,
                "confidence": record.confidence,
                "duration_ms": record.duration_ms
            })
        
        # Create edges for data flow
        for record in lineage:
            for input_ref in record.input_refs:
                edges.append({
                    "source": input_ref,
                    "target": record.id,
                    "type": "input"
                })
            for output_ref in record.output_refs:
                edges.append({
                    "source": record.id,
                    "target": output_ref,
                    "type": "output"
                })
        
        return {
            "nodes": nodes,
            "edges": edges,
            "root": reference
        }