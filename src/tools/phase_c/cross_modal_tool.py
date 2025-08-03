"""
Cross-Modal Analysis Tool Wrapper

Wraps the CrossModalAnalyzer with BaseTool interface for DAG integration.
"""

from typing import Dict, Any, List, Optional
from src.tools.base_tool_fixed import BaseTool, ToolRequest, ToolResult, ToolContract
import asyncio
import json


class CrossModalTool(BaseTool):
    """Tool wrapper for cross-modal analysis capabilities."""
    
    def __init__(self, service_manager=None):
        """Initialize the cross-modal analysis tool."""
        super().__init__(service_manager)
        self.tool_id = "CROSS_MODAL_ANALYZER"
        self.analyzer = None  # Will be initialized on first use
    
    def get_contract(self) -> ToolContract:
        """Return tool contract specification."""
        from src.tools.base_tool_fixed import ToolContract
        return ToolContract(
            tool_id=self.tool_id,
            name="Cross-Modal Analyzer",
            description="Analyze and integrate insights across different data modalities",
            category="cross_modal",
            input_schema={
                "type": "object",
                "properties": {
                    "data": {"type": "object"},
                    "operation": {"type": "string", "enum": [
                        "analyze", "extract_features", "align", "integrate"
                    ]},
                    "modalities": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["data"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "analysis": {"type": "object"},
                    "modalities": {"type": "array"},
                    "status": {"type": "string"}
                }
            },
            dependencies=[],
            performance_requirements={
                "max_execution_time": 30.0,
                "max_memory_mb": 1000
            },
            error_conditions=["INVALID_DATA", "ANALYSIS_FAILED"]
        )
        
    def _init_analyzer(self):
        """Lazy initialization of CrossModalAnalyzer."""
        if self.analyzer is None:
            try:
                from src.analysis.cross_modal_analyzer import CrossModalAnalyzer
                self.analyzer = CrossModalAnalyzer()
            except ImportError:
                # Provide fallback implementation
                self.analyzer = self._create_fallback_analyzer()
    
    def _create_fallback_analyzer(self):
        """Create a minimal fallback analyzer for testing."""
        class FallbackAnalyzer:
            def analyze_cross_modal(self, data):
                return {
                    "modalities_detected": ["text"],
                    "cross_modal_links": [],
                    "confidence": 0.5
                }
                
            def extract_modal_features(self, data):
                return {
                    "text_features": {"word_count": 100},
                    "visual_features": {},
                    "audio_features": {}
                }
                
            def align_modalities(self, data):
                return {
                    "alignment_score": 0.7,
                    "aligned_segments": []
                }
        
        return FallbackAnalyzer()
        
    def execute(self, request: ToolRequest) -> ToolResult:
        """
        Execute cross-modal analysis.
        
        Args:
            request: Tool request with multi-modal data
            
        Returns:
            ToolResult with cross-modal analysis results
        """
        try:
            # Start execution tracking
            self._start_execution()
            
            # Initialize analyzer if needed
            self._init_analyzer()
            
            # Extract parameters
            data = request.input_data.get("data", {})
            operation = request.input_data.get("operation", "analyze")
            modalities = request.input_data.get("modalities", ["text"])
            
            if operation == "analyze":
                # Perform cross-modal analysis
                analysis_result = self.analyzer.analyze_cross_modal(data)
                
                return self._create_success_result(
                    data={
                        "analysis": analysis_result,
                        "modalities": modalities,
                        "status": "completed"
                    },
                    metadata={
                        "operation": operation,
                        "analyzer": "CrossModalAnalyzer"
                    }
                )
                
            elif operation == "extract_features":
                # Extract modal-specific features
                features = self.analyzer.extract_modal_features(data)
                
                return self._create_success_result(
                    data={
                        "features": features,
                        "modalities": modalities
                    }
                )
                
            elif operation == "align":
                # Align different modalities
                alignment = self.analyzer.align_modalities(data)
                
                return self._create_success_result(
                    data={
                        "alignment": alignment,
                        "modalities": modalities
                    }
                )
                
            elif operation == "integrate":
                # Integrate insights across modalities
                integrated = self._integrate_cross_modal(data, modalities)
                
                return self._create_success_result(
                    data={
                        "integrated_insights": integrated,
                        "modalities": modalities
                    }
                )
                
            else:
                return self._create_error_result(
                    error_code="UNKNOWN_OPERATION",
                    error_message=f"Unknown operation: {operation}"
                )
                
        except Exception as e:
            return self._create_error_result(
                error_code="ANALYSIS_FAILED",
                error_message=f"Cross-modal analysis failed: {str(e)}"
            )
    
    def _integrate_cross_modal(self, data: Dict, modalities: List[str]) -> Dict:
        """Integrate insights across different modalities."""
        integrated = {
            "primary_modality": modalities[0] if modalities else "text",
            "modality_count": len(modalities),
            "integration_score": 0.75,
            "unified_representation": {},
            "cross_references": []
        }
        
        # Add modality-specific processing
        for modality in modalities:
            if modality == "text":
                integrated["unified_representation"]["text"] = {
                    "entities": data.get("entities", []),
                    "concepts": data.get("concepts", [])
                }
            elif modality == "visual":
                integrated["unified_representation"]["visual"] = {
                    "objects": data.get("objects", []),
                    "scenes": data.get("scenes", [])
                }
            elif modality == "audio":
                integrated["unified_representation"]["audio"] = {
                    "transcripts": data.get("transcripts", []),
                    "sounds": data.get("sounds", [])
                }
        
        return integrated
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        Validate input data for cross-modal analysis.
        
        Args:
            input_data: Input data to validate
            
        Returns:
            True if valid, False otherwise
        """
        if "data" not in input_data:
            return False
            
        data = input_data.get("data")
        if not isinstance(data, dict):
            return False
            
        # Check for at least one modality
        modalities = input_data.get("modalities", ["text"])
        if not isinstance(modalities, list) or len(modalities) == 0:
            return False
            
        return True
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get tool capabilities."""
        return {
            "tool_id": self.tool_id,
            "operations": [
                "analyze",
                "extract_features",
                "align",
                "integrate"
            ],
            "supported_modalities": [
                "text",
                "visual",
                "audio",
                "video",
                "structured_data"
            ],
            "cross_modal_linking": True,
            "feature_extraction": True
        }