"""T110: Provenance Service - Minimal Implementation

Tracks operation lineage and enables impact analysis.
Records all tool executions with input/output relationships.

This is a MINIMAL implementation focusing on:
- Basic operation recording
- Simple lineage tracking
- Input/output relationship capture
- Tool execution metadata

Deferred features:
- Impact analysis algorithms
- Cascading dependency tracking
- Complex lineage queries
- Performance optimization
"""

from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime
import uuid
import json


@dataclass
class Operation:
    """A single tool execution record."""
    id: str
    tool_id: str  # Tool that performed the operation
    operation_type: str  # Type of operation (create, update, delete, query)
    inputs: List[str]  # References to input objects
    outputs: List[str]  # References to output objects  
    parameters: Dict[str, Any]  # Tool parameters used
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: str = "running"  # running, completed, failed
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProvenanceChain:
    """A chain of operations leading to an object."""
    target_ref: str  # Reference to final object
    operations: List[str]  # Operation IDs in chronological order
    depth: int  # Number of operations in chain
    confidence: float  # Lowest confidence in chain
    created_at: datetime = field(default_factory=datetime.now)


class ProvenanceService:
    """T110: Provenance Service - Operation tracking and lineage management."""
    
    def __init__(self):
        self.operations: Dict[str, Operation] = {}
        self.object_to_operations: Dict[str, Set[str]] = {}  # object_ref -> operation_ids
        self.operation_chains: Dict[str, ProvenanceChain] = {}  # object_ref -> chain
        self.tool_stats: Dict[str, Dict[str, int]] = {}  # tool_id -> {calls, successes, failures}
    
    def start_operation(
        self,
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
            
        Returns:
            Operation ID for tracking
        """
        try:
            # Input validation
            if not tool_id or not operation_type:
                raise ValueError("tool_id and operation_type are required")
            
            if not isinstance(inputs, list):
                inputs = []
                
            if parameters is None:
                parameters = {}
            
            # Create operation record
            operation_id = f"op_{uuid.uuid4().hex[:8]}"
            operation = Operation(
                id=operation_id,
                tool_id=tool_id,
                operation_type=operation_type,
                inputs=inputs,
                outputs=[],  # Will be populated when operation completes
                parameters=parameters.copy(),
                started_at=datetime.now()
            )
            
            self.operations[operation_id] = operation
            
            # Update tool statistics
            if tool_id not in self.tool_stats:
                self.tool_stats[tool_id] = {"calls": 0, "successes": 0, "failures": 0}
            self.tool_stats[tool_id]["calls"] += 1
            
            # Link inputs to this operation
            for input_ref in inputs:
                if input_ref not in self.object_to_operations:
                    self.object_to_operations[input_ref] = set()
                self.object_to_operations[input_ref].add(operation_id)
            
            return operation_id
            
        except Exception as e:
            # Return a failed operation ID for error tracking
            error_op_id = f"op_error_{uuid.uuid4().hex[:8]}"
            error_operation = Operation(
                id=error_op_id,
                tool_id=tool_id,
                operation_type=operation_type,
                inputs=inputs,
                outputs=[],
                parameters=parameters or {},
                started_at=datetime.now(),
                completed_at=datetime.now(),
                status="failed",
                error_message=f"Failed to start operation: {str(e)}"
            )
            self.operations[error_op_id] = error_operation
            return error_op_id
    
    def complete_operation(
        self,
        operation_id: str,
        outputs: List[str],
        success: bool = True,
        error_message: Optional[str] = None,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Complete an operation and record outputs.
        
        Args:
            operation_id: Operation to complete
            outputs: List of output object references
            success: Whether operation succeeded
            error_message: Error message if failed
            metadata: Additional metadata
            
        Returns:
            Operation completion status
        """
        try:
            if operation_id not in self.operations:
                return {
                    "status": "error",
                    "error": f"Operation {operation_id} not found"
                }
            
            operation = self.operations[operation_id]
            
            # Update operation
            operation.outputs = outputs if outputs else []
            operation.completed_at = datetime.now()
            operation.status = "completed" if success else "failed"
            operation.error_message = error_message
            operation.metadata = metadata if metadata else {}
            
            # Update tool statistics
            tool_id = operation.tool_id
            if success:
                self.tool_stats[tool_id]["successes"] += 1
            else:
                self.tool_stats[tool_id]["failures"] += 1
            
            # Link outputs to this operation
            for output_ref in operation.outputs:
                if output_ref not in self.object_to_operations:
                    self.object_to_operations[output_ref] = set()
                self.object_to_operations[output_ref].add(operation_id)
                
                # Create/update provenance chain for output
                self._update_provenance_chain(output_ref, operation_id)
            
            return {
                "status": "success",
                "operation_id": operation_id,
                "duration_seconds": (
                    operation.completed_at - operation.started_at
                ).total_seconds(),
                "outputs_count": len(operation.outputs)
            }
            
        except Exception as e:
            return {
                "status": "error", 
                "error": f"Failed to complete operation: {str(e)}"
            }
    
    def _update_provenance_chain(self, object_ref: str, operation_id: str):
        """Update the provenance chain for an object."""
        try:
            operation = self.operations[operation_id]
            
            # Find the longest input chain
            input_chains = []
            for input_ref in operation.inputs:
                if input_ref in self.operation_chains:
                    input_chains.append(self.operation_chains[input_ref])
            
            # Create new chain
            if input_chains:
                # Use the longest input chain as base
                longest_chain = max(input_chains, key=lambda x: x.depth)
                new_operations = longest_chain.operations + [operation_id]
                new_depth = longest_chain.depth + 1
                # Chain confidence is minimum of all operations
                new_confidence = min(longest_chain.confidence, 0.95)  # Slight degradation
            else:
                # This is a root object
                new_operations = [operation_id]
                new_depth = 1
                new_confidence = 0.95  # High confidence for root objects
            
            self.operation_chains[object_ref] = ProvenanceChain(
                target_ref=object_ref,
                operations=new_operations,
                depth=new_depth,
                confidence=new_confidence
            )
            
        except Exception:
            # Silently fail - provenance chain creation is not critical
            pass
    
    def get_lineage(self, object_ref: str, max_depth: int = 10) -> Dict[str, Any]:
        """Get the lineage chain for an object.
        
        Args:
            object_ref: Reference to object
            max_depth: Maximum depth to traverse
            
        Returns:
            Lineage information
        """
        try:
            if object_ref not in self.operation_chains:
                return {
                    "status": "not_found",
                    "object_ref": object_ref,
                    "lineage": []
                }
            
            chain = self.operation_chains[object_ref]
            lineage = []
            
            # Build lineage from operations
            for i, op_id in enumerate(chain.operations):
                if i >= max_depth:
                    break
                    
                operation = self.operations.get(op_id)
                if operation:
                    lineage.append({
                        "operation_id": operation.id,
                        "tool_id": operation.tool_id,
                        "operation_type": operation.operation_type,
                        "started_at": operation.started_at.isoformat(),
                        "completed_at": operation.completed_at.isoformat() if operation.completed_at else None,
                        "status": operation.status,
                        "inputs": operation.inputs,
                        "outputs": operation.outputs
                    })
            
            return {
                "status": "success",
                "object_ref": object_ref,
                "depth": chain.depth,
                "confidence": chain.confidence,
                "lineage": lineage
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to get lineage: {str(e)}"
            }
    
    def get_operation(self, operation_id: str) -> Optional[Dict[str, Any]]:
        """Get details of a specific operation."""
        try:
            operation = self.operations.get(operation_id)
            if not operation:
                return None
            
            duration = None
            if operation.completed_at:
                duration = (operation.completed_at - operation.started_at).total_seconds()
            
            return {
                "operation_id": operation.id,
                "tool_id": operation.tool_id,
                "operation_type": operation.operation_type,
                "inputs": operation.inputs,
                "outputs": operation.outputs,
                "parameters": operation.parameters,
                "started_at": operation.started_at.isoformat(),
                "completed_at": operation.completed_at.isoformat() if operation.completed_at else None,
                "status": operation.status,
                "error_message": operation.error_message,
                "duration_seconds": duration,
                "metadata": operation.metadata
            }
            
        except Exception:
            return None
    
    def get_operations_for_object(self, object_ref: str) -> List[Dict[str, Any]]:
        """Get all operations that touched an object."""
        try:
            if object_ref not in self.object_to_operations:
                return []
            
            operations = []
            for op_id in self.object_to_operations[object_ref]:
                op_details = self.get_operation(op_id)
                if op_details:
                    operations.append(op_details)
            
            # Sort by start time
            operations.sort(key=lambda x: x["started_at"])
            return operations
            
        except Exception:
            return []
    
    def get_tool_statistics(self) -> Dict[str, Any]:
        """Get statistics about tool usage."""
        try:
            stats = {}
            for tool_id, tool_stats in self.tool_stats.items():
                success_rate = 0.0
                if tool_stats["calls"] > 0:
                    success_rate = tool_stats["successes"] / tool_stats["calls"]
                
                stats[tool_id] = {
                    "total_calls": tool_stats["calls"],
                    "successes": tool_stats["successes"],
                    "failures": tool_stats["failures"],
                    "success_rate": success_rate
                }
            
            return {
                "status": "success",
                "tool_statistics": stats,
                "total_operations": len(self.operations),
                "total_objects_tracked": len(self.object_to_operations)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to get statistics: {str(e)}"
            }
    
    def cleanup_old_operations(self, days_old: int = 30) -> Dict[str, Any]:
        """Remove operations older than specified days."""
        try:
            cutoff_date = datetime.now() - datetime.timedelta(days=days_old)
            removed_count = 0
            
            # Find old operations
            old_operation_ids = []
            for op_id, operation in self.operations.items():
                if operation.started_at < cutoff_date:
                    old_operation_ids.append(op_id)
            
            # Remove operations and update indices
            for op_id in old_operation_ids:
                operation = self.operations[op_id]
                
                # Remove from object-to-operations mapping
                for obj_ref in operation.inputs + operation.outputs:
                    if obj_ref in self.object_to_operations:
                        self.object_to_operations[obj_ref].discard(op_id)
                        if not self.object_to_operations[obj_ref]:
                            del self.object_to_operations[obj_ref]
                
                # Remove operation
                del self.operations[op_id]
                removed_count += 1
            
            return {
                "status": "success",
                "removed_operations": removed_count,
                "cutoff_date": cutoff_date.isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to cleanup: {str(e)}"
            }
    
    def get_tool_info(self):
        """Return tool information for audit system"""
        return {
            "tool_id": "PROVENANCE_SERVICE",
            "tool_type": "CORE_SERVICE",
            "status": "functional",
            "description": "Operation lineage and impact tracking service",
            "features": {
                "operation_tracking": True,
                "lineage_analysis": True,
                "metadata_capture": True
            },
            "stats": self.get_tool_statistics()
        }