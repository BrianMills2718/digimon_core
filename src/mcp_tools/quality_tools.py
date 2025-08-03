"""
Quality Service MCP Tools

T111: Quality Service tools for confidence assessment and propagation.
"""

import logging
from typing import Dict, Any, List, Optional
from fastmcp import FastMCP

from .server_config import get_mcp_config

logger = logging.getLogger(__name__)


class QualityServiceTools:
    """Collection of Quality Service tools for MCP server"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config = get_mcp_config()
    
    @property
    def quality_service(self):
        """Get quality service instance"""
        return self.config.quality_service
    
    def register_tools(self, mcp: FastMCP):
        """Register all quality service tools with MCP server"""
        
        @mcp.tool()
        def assess_confidence(
            object_ref: str,
            assessment_type: str,
            evidence: Dict[str, Any],
            metadata: Dict[str, Any] = None
        ) -> Dict[str, Any]:
            """Assess confidence for an object.
            
            Args:
                object_ref: Reference to the object being assessed
                assessment_type: Type of assessment (entity_extraction, relationship_extraction, etc.)
                evidence: Evidence supporting the assessment
                metadata: Additional metadata
            """
            try:
                if not self.quality_service:
                    return {"error": "Quality service not available"}
                
                return self.quality_service.assess_confidence(
                    object_ref=object_ref,
                    assessment_type=assessment_type,
                    evidence=evidence,
                    metadata=metadata or {}
                )
            except Exception as e:
                self.logger.error(f"Error assessing confidence: {e}")
                return {"error": str(e)}
        
        @mcp.tool()
        def propagate_confidence(
            source_ref: str,
            target_refs: List[str],
            propagation_rule: str = "conservative",
            metadata: Dict[str, Any] = None
        ) -> Dict[str, Any]:
            """Propagate confidence from source to targets.
            
            Args:
                source_ref: Source object reference
                target_refs: List of target object references
                propagation_rule: Rule for propagation (conservative, optimistic, weighted)
                metadata: Additional metadata
            """
            try:
                if not self.quality_service:
                    return {"error": "Quality service not available"}
                
                return self.quality_service.propagate_confidence(
                    source_ref=source_ref,
                    target_refs=target_refs,
                    propagation_rule=propagation_rule,
                    metadata=metadata or {}
                )
            except Exception as e:
                self.logger.error(f"Error propagating confidence: {e}")
                return {"error": str(e)}
        
        @mcp.tool()
        def get_quality_assessment(object_ref: str) -> Optional[Dict[str, Any]]:
            """Get quality assessment for an object.
            
            Args:
                object_ref: Reference to the object
            """
            try:
                if not self.quality_service:
                    return {"error": "Quality service not available"}
                
                return self.quality_service.get_quality_assessment(object_ref)
            except Exception as e:
                self.logger.error(f"Error getting quality assessment: {e}")
                return {"error": str(e)}
        
        @mcp.tool()
        def get_confidence_trend(object_ref: str) -> Dict[str, Any]:
            """Get confidence trend over time for an object.
            
            Args:
                object_ref: Reference to the object
            """
            try:
                if not self.quality_service:
                    return {"error": "Quality service not available"}
                
                return self.quality_service.get_confidence_trend(object_ref)
            except Exception as e:
                self.logger.error(f"Error getting confidence trend: {e}")
                return {"error": str(e)}
        
        @mcp.tool()
        def filter_by_quality(
            object_refs: List[str],
            min_confidence: float = 0.5,
            quality_tier: str = "any"
        ) -> Dict[str, Any]:
            """Filter objects by quality thresholds.
            
            Args:
                object_refs: List of object references to filter
                min_confidence: Minimum confidence threshold
                quality_tier: Quality tier filter (high, medium, low, any)
            """
            try:
                if not self.quality_service:
                    return {"error": "Quality service not available"}
                
                # Import QualityTier enum
                from src.core.quality_service import QualityTier
                
                # Convert string to enum
                tier_mapping = {
                    "high": QualityTier.HIGH,
                    "medium": QualityTier.MEDIUM,
                    "low": QualityTier.LOW,
                    "any": None
                }
                
                tier_filter = tier_mapping.get(quality_tier.lower())
                
                return self.quality_service.filter_by_quality(
                    object_refs=object_refs,
                    min_confidence=min_confidence,
                    quality_tier=tier_filter
                )
            except Exception as e:
                self.logger.error(f"Error filtering by quality: {e}")
                return {"error": str(e)}
        
        @mcp.tool()
        def get_quality_statistics() -> Dict[str, Any]:
            """Get quality service statistics."""
            try:
                if not self.quality_service:
                    return {"error": "Quality service not available"}
                
                return self.quality_service.get_stats()
            except Exception as e:
                self.logger.error(f"Error getting quality statistics: {e}")
                return {"error": str(e)}
        
        self.logger.info("Quality service tools registered successfully")
    
    def get_tool_info(self) -> Dict[str, Any]:
        """Get information about quality service tools"""
        return {
            "service": "T111_Quality_Service",
            "tool_count": 6,
            "tools": [
                "assess_confidence",
                "propagate_confidence",
                "get_quality_assessment",
                "get_confidence_trend",
                "filter_by_quality",
                "get_quality_statistics"
            ],
            "description": "Confidence assessment and quality management tools",
            "capabilities": [
                "confidence_assessment",
                "confidence_propagation",
                "quality_filtering",
                "trend_analysis",
                "statistics_reporting"
            ],
            "service_available": self.quality_service is not None
        }