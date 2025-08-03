"""
Collaborative Intelligence Framework - Task C.6

Multi-agent reasoning with conflict resolution and consensus building.
"""

from .multi_agent_coordinator import MultiAgentCoordinator, Agent, Task, AgentResult
from .agent_specializer import AgentSpecializer, SpecializedAgent
from .conflict_resolver import ConflictResolver, Conflict
from .consensus_builder import ConsensusBuilder

__all__ = [
    "MultiAgentCoordinator",
    "Agent",
    "Task",
    "AgentResult",
    "AgentSpecializer",
    "SpecializedAgent",
    "ConflictResolver",
    "Conflict",
    "ConsensusBuilder"
]