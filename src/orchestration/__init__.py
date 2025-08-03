"""
Agent Orchestration System for KGAS

A flexible, minimal agent orchestration system that enables immediate agent coordination
while maintaining the ability to completely change orchestration approaches in the future.

Core Components:
- Base interfaces for agents and orchestrators
- MCP tool adapter for existing KGAS infrastructure
- Memory-aware agents with learning capabilities (Phase 1: Advanced Agent Features)
- Simple agent implementations
- Configuration-driven orchestrator
- Factory pattern for easy pivoting
- Memory system with debugging tools

Advanced Features (Phase 1 Complete):
- AgentMemory: Persistent memory with episodic, semantic, procedural, and working memory
- MemoryAwareAgent: Base class for agents that learn from experience
- Memory debugging and visualization tools
- Parameter recommendations and strategy learning
"""

from .base import Agent, Orchestrator, Task, Result
from .factory import create_orchestrator, initialize_orchestration_system

# Memory system components (Phase 1: Advanced Agent Features)
from .memory import AgentMemory, MemoryType, MemoryQuery
from .memory_agent import MemoryAwareAgent
from .memory_debug import MemoryDebugger, MemoryVisualizer, debug_agent_memory, cleanup_agent_memory

__all__ = [
    # Core orchestration
    "Agent",
    "Orchestrator", 
    "Task",
    "Result",
    "create_orchestrator",
    "initialize_orchestration_system",
    
    # Memory system (Phase 1: Advanced Agent Features)
    "AgentMemory",
    "MemoryType", 
    "MemoryQuery",
    "MemoryAwareAgent",
    "MemoryDebugger",
    "MemoryVisualizer",
    "debug_agent_memory",
    "cleanup_agent_memory"
]