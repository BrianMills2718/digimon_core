"""
Consensus Builder for Multi-Agent Agreement
"""

import logging
from typing import List, Dict, Any
from collections import Counter

logger = logging.getLogger(__name__)


class ConsensusBuilder:
    """Builds consensus from multiple agent opinions"""
    
    def __init__(self):
        self.logger = logger
        
    async def build_consensus(self,
                             opinions: List[Dict[str, Any]],
                             method: str = "weighted_voting") -> Dict[str, Any]:
        """Build consensus from agent opinions"""
        self.logger.info(f"Building consensus from {len(opinions)} opinions using {method}")
        
        if not opinions:
            return {
                "final_assessment": "no_data",
                "agreement_score": 0,
                "dissenting_opinions": []
            }
        
        if method == "weighted_voting":
            return await self._weighted_voting_consensus(opinions)
        elif method == "majority":
            return await self._majority_consensus(opinions)
        else:
            return await self._simple_consensus(opinions)
    
    async def _weighted_voting_consensus(self, opinions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build consensus using weighted voting"""
        # Weight votes by confidence
        vote_weights = {}
        
        for opinion in opinions:
            assessment = opinion["assessment"]
            confidence = opinion["confidence"]
            
            if assessment not in vote_weights:
                vote_weights[assessment] = 0
            vote_weights[assessment] += confidence
        
        # Find winning assessment
        final_assessment = max(vote_weights.items(), key=lambda x: x[1])[0]
        
        # Calculate agreement score
        total_weight = sum(vote_weights.values())
        winning_weight = vote_weights[final_assessment]
        agreement_score = winning_weight / total_weight if total_weight > 0 else 0
        
        # Identify dissenting opinions
        dissenting = []
        for opinion in opinions:
            if opinion["assessment"] != final_assessment:
                dissenting.append({
                    "agent": opinion["agent"],
                    "assessment": opinion["assessment"],
                    "confidence": opinion["confidence"]
                })
        
        return {
            "final_assessment": final_assessment,
            "agreement_score": agreement_score,
            "dissenting_opinions": dissenting,
            "vote_distribution": vote_weights
        }
    
    async def _majority_consensus(self, opinions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build consensus using simple majority"""
        assessments = [op["assessment"] for op in opinions]
        counter = Counter(assessments)
        
        # Get most common assessment
        final_assessment = counter.most_common(1)[0][0]
        agreement_count = counter[final_assessment]
        
        return {
            "final_assessment": final_assessment,
            "agreement_score": agreement_count / len(opinions),
            "dissenting_opinions": [op for op in opinions if op["assessment"] != final_assessment]
        }
    
    async def _simple_consensus(self, opinions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Simple consensus - first opinion wins"""
        return {
            "final_assessment": opinions[0]["assessment"],
            "agreement_score": 1.0 / len(opinions),
            "dissenting_opinions": opinions[1:]
        }