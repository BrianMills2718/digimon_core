"""
Conflict Resolver for Multi-Agent Systems
"""

import logging
from typing import List, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass 
class Conflict:
    """Represents a conflict between agents"""
    agent1_id: str
    agent2_id: str
    claim1: str
    claim2: str
    conflict_type: str  # "contradiction", "inconsistency", "uncertainty"
    severity: float


class ConflictResolver:
    """Detects and resolves conflicts between agent results"""
    
    def __init__(self):
        self.logger = logger
        
    async def detect_conflicts(self, agent_results: List[Dict[str, Any]]) -> List[Conflict]:
        """Detect conflicts between agent results"""
        self.logger.info(f"Detecting conflicts among {len(agent_results)} agent results")
        
        conflicts = []
        
        # Compare each pair of results
        for i, result1 in enumerate(agent_results):
            for result2 in agent_results[i+1:]:
                # Check for contradictions
                if self._are_contradictory(result1["claim"], result2["claim"]):
                    conflicts.append(Conflict(
                        agent1_id=result1["agent_id"],
                        agent2_id=result2["agent_id"],
                        claim1=result1["claim"],
                        claim2=result2["claim"],
                        conflict_type="contradiction",
                        severity=0.8
                    ))
        
        return conflicts
    
    async def resolve_conflicts(self, conflicts: List[Conflict]) -> Dict[str, Any]:
        """Resolve detected conflicts"""
        self.logger.info(f"Resolving {len(conflicts)} conflicts")
        
        if not conflicts:
            return {
                "strategy": "none_needed",
                "final_claim": "No conflicts detected",
                "confidence": 1.0
            }
        
        # Analyze conflict patterns
        contradiction_count = sum(1 for c in conflicts if c.conflict_type == "contradiction")
        
        # Choose resolution strategy
        if contradiction_count > len(conflicts) / 2:
            # Many contradictions - use weighted average
            strategy = "weighted_average"
            final_claim = "Mixed evidence with contradictory viewpoints"
            confidence = 0.6
        else:
            # Few contradictions - use consensus
            strategy = "consensus"
            final_claim = "Consensus reached with minor disagreements"
            confidence = 0.8
        
        return {
            "strategy": strategy,
            "final_claim": final_claim,
            "confidence": confidence,
            "conflicts_resolved": len(conflicts)
        }
    
    def _are_contradictory(self, claim1: str, claim2: str) -> bool:
        """Check if two claims are contradictory"""
        # Simple keyword-based contradiction detection
        positive_keywords = ["will", "can", "effective", "breakthrough"]
        negative_keywords = ["won't", "cannot", "exaggerated", "threats", "critics"]
        
        claim1_positive = any(word in claim1.lower() for word in positive_keywords)
        claim1_negative = any(word in claim1.lower() for word in negative_keywords)
        
        claim2_positive = any(word in claim2.lower() for word in positive_keywords)
        claim2_negative = any(word in claim2.lower() for word in negative_keywords)
        
        # Contradiction if one is positive and other is negative
        return (claim1_positive and claim2_negative) or (claim1_negative and claim2_positive)