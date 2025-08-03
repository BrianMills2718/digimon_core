"""
Agent Specializer for Task Routing
"""

import logging
from typing import Dict, Any, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class SpecializedAgent:
    """Represents a specialized agent"""
    agent_id: str
    specialization: str
    capabilities: List[str]
    performance_score: float = 1.0


class AgentSpecializer:
    """Routes tasks to specialized agents"""
    
    def __init__(self):
        self.logger = logger
        self.agents: Dict[str, SpecializedAgent] = {}
        
    async def initialize_agents(self, agent_types: List[str]):
        """Initialize specialized agents"""
        self.logger.info(f"Initializing {len(agent_types)} specialized agents")
        
        for agent_type in agent_types:
            agent_id = f"{agent_type}_001"
            
            # Define capabilities based on type
            capabilities = []
            if agent_type == "entity_extractor":
                capabilities = ["extract_entities", "identify_names", "find_organizations"]
            elif agent_type == "sentiment_analyzer":
                capabilities = ["analyze_sentiment", "detect_emotion", "measure_polarity"]
            elif agent_type == "fact_checker":
                capabilities = ["verify_facts", "check_consistency", "validate_claims"]
            
            self.agents[agent_id] = SpecializedAgent(
                agent_id=agent_id,
                specialization=agent_type,
                capabilities=capabilities
            )
    
    async def route_task(self, task: Dict[str, Any]) -> SpecializedAgent:
        """Route task to appropriate specialized agent"""
        task_type = task.get("type", "")
        
        # Find best matching agent
        for agent in self.agents.values():
            if task_type in agent.capabilities or task_type.replace("_", " ") in " ".join(agent.capabilities):
                self.logger.info(f"Routing task {task_type} to {agent.agent_id}")
                return agent
        
        # Default routing
        if self.agents:
            return list(self.agents.values())[0]
        
        # Create default agent if none exist
        return SpecializedAgent(
            agent_id="default_agent",
            specialization="general",
            capabilities=["general_processing"]
        )